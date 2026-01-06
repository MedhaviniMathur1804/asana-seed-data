"""
Task generator.

Creates tens of thousands of tasks across projects with:
- Realistic, context-aware titles.
- Non-uniform completion and overdue patterns.
- Business-day-weighted due dates.
- Optional assignees and sections.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from faker import Faker

from ..utils.config import TASK_CONFIG, VOLUME_CONFIG
from ..utils.dates import business_due_date_from_created, completed_after_created, is_overdue, random_datetime_between
from ..utils.db import bulk_insert
from ..utils.text import generate_task_title


def _build_team_members(projects: List[Dict[str, str]], memberships: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """Map team_id -> list of user_ids for assignment decisions."""
    team_to_users: Dict[str, List[str]] = {}
    for m in memberships:
        team_to_users.setdefault(m["team_id"], []).append(m["user_id"])
    return team_to_users


def _sections_by_project(sections: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    mapping: Dict[str, List[Dict[str, str]]] = {}
    for s in sections:
        mapping.setdefault(s["project_id"], []).append(s)
    return mapping


def _pick_section(sections: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    Prefer "work-in-flight" sections over Done/Backlog.

    This creates more realistic board distributions where active columns
    carry more tasks than terminal columns.
    """
    if not sections:
        return None
    weights = []
    for s in sections:
        name = s["name"].lower()
        if "backlog" in name or "ideas" in name:
            weights.append(0.8)
        elif "done" in name or "closed" in name or "complete" in name:
            weights.append(0.7)
        else:
            weights.append(2.0)  # emphasize in-progress stages
    return random.choices(sections, weights=weights, k=1)[0]


def _pick_assignee(
    project: Dict[str, str],
    team_members: Dict[str, List[str]],
    all_users: List[Dict[str, str]],
) -> Optional[str]:
    """
    Assign from the project’s team when possible, with some unassigned tasks.
    """
    if random.random() < TASK_CONFIG.unassigned_task_probability:
        return None

    team_id = project["team_id"]
    candidates = team_members.get(team_id)
    if not candidates:
        # Fallback to any user if team membership data is sparse.
        return random.choice(all_users)["id"]
    return random.choice(candidates)


def generate_tasks(
    conn,
    organization_id: str,
    projects: List[Dict[str, str]],
    sections: List[Dict[str, str]],
    users: List[Dict[str, str]],
    memberships: List[Dict[str, str]],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Create 40–120 tasks per project with corporate-like lifecycle patterns.
    """
    faker = faker or Faker("en_US")

    proj_to_sections = _sections_by_project(sections)
    team_members = _build_team_members(projects, memberships)
    all_users = users

    tasks: List[Dict[str, str]] = []
    rows = []
    now = datetime.utcnow()

    for project in projects:
        min_t, max_t = VOLUME_CONFIG.min_tasks_per_project, VOLUME_CONFIG.max_tasks_per_project
        mode = (min_t + max_t) / 2 + 10  # bias slightly higher than midpoint
        num_tasks = int(round(random.triangular(min_t, max_t, mode)))
        num_tasks = max(min_t, min(max_t, num_tasks))

        project_created = datetime.fromisoformat(project["created_at"])

        project_sections = proj_to_sections.get(project["id"], [])

        for _ in range(num_tasks):
            created_at = random_datetime_between(project_created, now)
            section = _pick_section(project_sections) if project_sections else None
            section_id = section["id"] if section else None

            assignee_id = _pick_assignee(project, team_members, all_users)

            # Assign due dates more frequently for roadmap/sprint/launch work.
            has_due = project["type"] in {"roadmap", "sprint", "launch"}
            if has_due and random.random() < 0.85:
                due_date = business_due_date_from_created(created_at, min_days=3, max_days=75)
            elif random.random() < 0.35:
                due_date = business_due_date_from_created(created_at, min_days=5, max_days=45)
            else:
                due_date = None

            # Completion decisions: globally ~60–70% completed.
            completed_flag = random.random() < TASK_CONFIG.completion_ratio
            completed_at = None
            if completed_flag:
                completed_at = completed_after_created(created_at, due_date)

            # Introduce a controlled fraction of overdue tasks.
            if due_date is not None and not completed_flag:
                # Only some incomplete tasks will truly be overdue.
                if random.random() < TASK_CONFIG.overdue_task_probability:
                    # If due_date not yet past, push it slightly into the past.
                    if due_date >= now.date():
                        due_date = now.date()

            last_activity_at = completed_at if completed_at else created_at

            name = generate_task_title(
                faker=faker,
                project_type=project["type"],
                section_name=section["name"] if section else None,
            )

            task_id = str(uuid.uuid4())

            rows.append(
                (
                    task_id,
                    project["id"],
                    section_id,
                    organization_id,
                    name,
                    None,  # description left for future extension
                    assignee_id,
                    assignee_id or random.choice(all_users)["id"],  # created_by: mostly assignee or teammate
                    created_at.isoformat(),
                    due_date.isoformat() if due_date else None,
                    completed_at.isoformat() if completed_at else None,
                    last_activity_at.isoformat(),
                    random.choice(["low", "medium", "high", "urgent"]),
                    0,
                )
            )
            tasks.append(
                {
                    "id": task_id,
                    "project_id": project["id"],
                    "section_id": section_id,
                    "assignee_id": assignee_id,
                    "created_at": created_at.isoformat(),
                    "due_date": due_date.isoformat() if due_date else None,
                    "completed_at": completed_at.isoformat() if completed_at else None,
                }
            )

    bulk_insert(
        conn,
        table="tasks",
        columns=[
            "id",
            "project_id",
            "section_id",
            "organization_id",
            "name",
            "description",
            "assignee_id",
            "created_by_user_id",
            "created_at",
            "due_date",
            "completed_at",
            "last_activity_at",
            "priority",
            "is_deleted",
        ],
        rows=rows,
    )

    return tasks


