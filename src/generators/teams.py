"""
Team generator.

We create functional teams with weighted selection to ensure core functions
(Engineering/Product/Design/Marketing/Sales) almost always appear, mirroring
real enterprise org charts.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from faker import Faker

from ..utils.config import VOLUME_CONFIG
from ..utils.db import bulk_insert


def _weighted_unique_sample(options: List[str], weights: List[float], target: int) -> List[str]:
    """
    Sample unique team names using weights (without replacement).

    We retry draws until we reach the requested count to preserve weighting
    without allowing duplicates.
    """
    chosen = []
    while len(chosen) < target and len(chosen) < len(options):
        pick = random.choices(options, weights=weights, k=1)[0]
        if pick not in chosen:
            chosen.append(pick)
    return chosen


def generate_teams(
    conn,
    organization: Dict[str, str],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Generate 8–15 teams with realistic functional coverage.

    We bias toward ~11 teams using a triangular distribution to emulate
    large-but-not-huge enterprise structures.
    """
    faker = faker or Faker("en_US")

    min_t, max_t = VOLUME_CONFIG.min_teams, VOLUME_CONFIG.max_teams
    target_teams = int(round(random.triangular(min_t, max_t, (min_t + max_t) / 2 + 2)))
    target_teams = max(min_t, min(max_t, target_teams))

    # Core functional areas appear more often; niche teams less so.
    base_names = [
        "Engineering",
        "Product",
        "Design",
        "Marketing",
        "Sales",
        "Customer Success",
        "Data",
        "IT",
        "Security",
        "Finance",
        "People Operations",
        "Recruiting",
        "Quality Assurance",
        "Business Operations",
        "Program Management",
    ]
    base_weights = [
        0.20,  # Engineering dominates headcount in many tech orgs
        0.14,  # Product partners closely with Engineering
        0.10,  # Design smaller but central
        0.10,  # Marketing mid-sized
        0.10,  # Sales sizable in enterprise
        0.06,  # Customer Success present but smaller
        0.05,  # Data/Analytics
        0.04,  # IT
        0.03,  # Security
        0.03,  # Finance
        0.03,  # People Ops
        0.03,  # Recruiting
        0.03,  # QA
        0.03,  # BizOps
        0.03,  # Program Mgmt
    ]

    picked_names = _weighted_unique_sample(base_names, base_weights, target_teams)

    # Spread team creation over the last 6–9 years after org founding.
    org_created = datetime.fromisoformat(organization["created_at"])
    team_records: List[Dict[str, str]] = []
    rows = []
    for name in picked_names:
        team_id = str(uuid.uuid4())
        years_after_org = random.uniform(0.5, 9.0)
        created_at = org_created + timedelta(days=365 * years_after_org)
        description = faker.catch_phrase()
        rows.append((team_id, organization["id"], name, description, created_at.isoformat()))
        team_records.append(
            {
                "id": team_id,
                "name": name,
                "created_at": created_at.isoformat(),
            }
        )

    bulk_insert(
        conn,
        table="teams",
        columns=["id", "organization_id", "name", "description", "created_at"],
        rows=rows,
    )

    return team_records


