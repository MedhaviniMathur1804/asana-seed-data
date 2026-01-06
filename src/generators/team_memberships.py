"""
Team membership generator.

Assigns each user to 1–3 teams with role-aware routing (engineers to
Engineering/Data, sales to Sales/CS, etc.) to mirror real organizational
structures.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from faker import Faker

from ..utils.db import bulk_insert


def _role_to_preferred_team_names(role: str) -> List[str]:
    """Map user role keywords to likely team buckets."""
    role_lower = role.lower()
    if "engineer" in role_lower and "qa" not in role_lower:
        return ["Engineering", "Security", "IT"]
    if "qa" in role_lower:
        return ["Quality Assurance", "Engineering"]
    if "product" in role_lower:
        return ["Product", "Program Management"]
    if "design" in role_lower:
        return ["Design"]
    if "data" in role_lower or "analyst" in role_lower:
        return ["Data"]
    if "sales" in role_lower:
        return ["Sales"]
    if "customer success" in role_lower or "account" in role_lower:
        return ["Customer Success", "Sales"]
    if "security" in role_lower:
        return ["Security", "Engineering"]
    if "it" in role_lower:
        return ["IT"]
    if "finance" in role_lower:
        return ["Finance", "Business Operations"]
    if "people" in role_lower or "recruit" in role_lower:
        return ["People Operations", "Recruiting"]
    if "program" in role_lower or "project" in role_lower:
        return ["Program Management", "Product"]
    return ["Business Operations"]


def _pick_membership_count() -> int:
    """
    Users typically belong to a single primary team; a minority straddle two.
    """
    return random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05], k=1)[0]


def _pick_membership_role(user_role: str) -> str:
    """
    Small fraction of memberships are leads, aligning with manager/staff titles.
    """
    role_lower = user_role.lower()
    is_manager_title = any(token in role_lower for token in ["manager", "lead", "staff"])
    if is_manager_title and random.random() > 0.3:
        return "lead"
    return "lead" if random.random() < 0.07 else "member"


def generate_team_memberships(
    conn,
    teams: List[Dict[str, str]],
    users: List[Dict[str, str]],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Assign each user to 1–3 teams, steering toward role-aligned teams when present.

    We spread added_at dates across the last few years after org formation to
    simulate staggered hiring and team growth.
    """
    faker = faker or Faker("en_US")

    team_by_name = {t["name"]: t for t in teams}
    team_ids = [t["id"] for t in teams]
    rows = []
    memberships: List[Dict[str, str]] = []

    now = datetime.utcnow()
    for user in users:
        desired = _pick_membership_count()
        preferred_names = _role_to_preferred_team_names(user["role"])

        # Build candidate team IDs prioritizing preferred teams.
        preferred_ids = [team_by_name[name]["id"] for name in preferred_names if name in team_by_name]
        remaining_ids = [tid for tid in team_ids if tid not in preferred_ids]

        # Guarantee at least one assignment; fill with remaining teams if needed.
        chosen: List[str] = []
        for tid in preferred_ids:
            if len(chosen) >= desired:
                break
            chosen.append(tid)

        if len(chosen) < desired:
            extras = random.sample(remaining_ids, k=min(len(remaining_ids), desired - len(chosen)))
            chosen.extend(extras)

        # If still none (edge case), fallback to any random team.
        if not chosen and team_ids:
            chosen = [random.choice(team_ids)]

        added_at = now - timedelta(days=random.randint(30, 900))
        membership_role = _pick_membership_role(user["role"])

        for tid in chosen:
            membership_id = str(uuid.uuid4())
            rows.append((membership_id, tid, user["id"], membership_role, added_at.isoformat()))
            memberships.append(
                {
                    "id": membership_id,
                    "team_id": tid,
                    "user_id": user["id"],
                    "role": membership_role,
                }
            )

    bulk_insert(
        conn,
        table="team_memberships",
        columns=["id", "team_id", "user_id", "role", "added_at"],
        rows=rows,
    )

    return memberships


