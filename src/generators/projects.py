"""
Project generator.

Creates multiple projects per team with realistic naming and type mix
(roadmap, sprint, launch, ops). Dates respect team creation times.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from faker import Faker

from ..utils.config import VOLUME_CONFIG
from ..utils.db import bulk_insert


PROJECT_TYPES = [
    ("roadmap", 0.25),
    ("sprint", 0.35),
    ("launch", 0.20),
    ("ops", 0.20),
]


def _pick_project_type() -> str:
    labels, weights = zip(*PROJECT_TYPES)
    return random.choices(labels, weights=weights, k=1)[0]


def _name_project(faker: Faker, ptype: str, team_name: str) -> str:
    """
    Generate human-like project names with light templating.

    - Roadmaps emphasize quarters/years.
    - Sprints use numbered/dated names.
    - Launches use feature or market labels.
    - Ops use stability/maintenance phrasing.
    """
    if ptype == "roadmap":
        quarter = random.choice(["Q1", "Q2", "Q3", "Q4"])
        year = datetime.utcnow().year + random.choice([0, 1])
        return f"{team_name} {quarter} {year} Roadmap"
    if ptype == "sprint":
        sprint_num = random.randint(12, 58)
        codename = random.choice(["Orion", "Nova", "Atlas", "Vega", "Helix", "Quasar"])
        return f"Sprint {sprint_num} - {codename}"
    if ptype == "launch":
        feature = faker.bs().title()
        market = random.choice(["Enterprise", "SMB", "EMEA", "US", "APAC"])
        return f"{feature} Launch - {market}"
    # ops
    theme = random.choice(["Reliability", "SRE", "Incident Readiness", "Data Hygiene", "Automation"])
    return f"{team_name} {theme} Ops"


def generate_projects(
    conn,
    organization_id: str,
    teams: List[Dict[str, str]],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Generate 3–10 projects per team using weighted project types.

    Creation dates trail team creation to reflect team ramp-up.
    """
    faker = faker or Faker("en_US")

    min_p, max_p = VOLUME_CONFIG.min_projects_per_team, VOLUME_CONFIG.max_projects_per_team
    projects: List[Dict[str, str]] = []
    rows = []

    for team in teams:
        count = int(round(random.triangular(min_p, max_p, (min_p + max_p) / 2 + 1)))
        count = max(min_p, min(max_p, count))

        team_created = datetime.fromisoformat(team["created_at"])

        for _ in range(count):
            ptype = _pick_project_type()
            name = _name_project(faker, ptype, team["name"])
            project_id = str(uuid.uuid4())

            # Start after team creation; allow some projects to be newer.
            days_after_team = random.randint(30, 900)
            created_at = team_created + timedelta(days=days_after_team)

            # Roadmaps and launches tend to have due dates; ops may not.
            due_date = None
            if ptype in {"roadmap", "launch"}:
                due_date = (created_at + timedelta(days=random.randint(60, 240))).date().isoformat()

            rows.append(
                (
                    project_id,
                    team["id"],
                    organization_id,
                    name,
                    faker.sentence(nb_words=10),
                    ptype,
                    created_at.date().isoformat(),
                    due_date,
                    created_at.isoformat(),
                    None,
                    0,
                )
            )
            projects.append(
                {
                    "id": project_id,
                    "team_id": team["id"],
                    "name": name,
                    "type": ptype,
                    "created_at": created_at.isoformat(),
                }
            )

    bulk_insert(
        conn,
        table="projects",
        columns=[
            "id",
            "team_id",
            "organization_id",
            "name",
            "description",
            "project_type",
            "start_date",
            "due_date",
            "created_at",
            "completed_at",
            "is_archived",
        ],
        rows=rows,
    )

    return projects


