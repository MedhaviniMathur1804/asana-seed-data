"""
Organization generator.

We keep this separate to mirror Asana's top-level org entity even though we
generate only one. Returning IDs keeps downstream generators decoupled.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

from faker import Faker

from ..utils.config import ORG_CONFIG
from ..utils.db import bulk_insert


def generate_organization(conn, faker: Optional[Faker] = None) -> Dict[str, str]:
    """
    Create a single realistic organization.

    We place the org creation 8–15 years in the past to reflect a mature
    enterprise that has grown to thousands of users.
    """
    faker = faker or Faker("en_US")

    org_id = str(uuid.uuid4())
    years_ago = faker.random_int(min=8, max=15)
    created_at = datetime.utcnow() - timedelta(days=365 * years_ago)

    rows = [
        (
            org_id,
            ORG_CONFIG.name,
            ORG_CONFIG.domain,
            created_at.isoformat(),
        )
    ]

    bulk_insert(
        conn,
        table="organizations",
        columns=["id", "name", "domain", "created_at"],
        rows=rows,
    )

    return {"id": org_id, "created_at": created_at.isoformat()}


