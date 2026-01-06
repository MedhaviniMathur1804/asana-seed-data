"""
Section generator.

Creates Asana-like workflow columns per project. Not all projects share the
same sections to reflect team-specific workflows.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from faker import Faker

from ..utils.db import bulk_insert


SECTION_TEMPLATES = [
    ["Backlog", "Next Up", "In Progress", "Review", "Done"],
    ["Todo", "Doing", "Blocked", "Ready for QA", "Done"],
    ["Ideas", "Prioritized", "Building", "Testing", "Launched"],
    ["Intake", "Triaged", "In Progress", "Validation", "Closed"],
    ["Pipeline", "Discovery", "Execution", "UAT", "Complete"],
]


def generate_sections(
    conn,
    projects: List[Dict[str, str]],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Assign a section template to each project with slight variability.

    Some projects (e.g., ops) may have leaner boards; we randomly drop one
    middle column in a minority of cases to reflect bespoke workflows.
    """
    faker = faker or Faker("en_US")

    rows = []
    sections: List[Dict[str, str]] = []

    for project in projects:
        template = random.choice(SECTION_TEMPLATES)

        # For ops-type projects, occasionally shorten the workflow.
        names = list(template)
        if project["type"] == "ops" and len(names) > 4 and random.random() < 0.4:
            drop_idx = random.randint(1, len(names) - 2)  # drop a middle stage
            names.pop(drop_idx)

        created_at = datetime.fromisoformat(project["created_at"])
        for order, name in enumerate(names):
            section_id = str(uuid.uuid4())
            section_created = created_at + timedelta(days=random.randint(0, 60))
            rows.append(
                (
                    section_id,
                    project["id"],
                    name,
                    order,
                    section_created.isoformat(),
                )
            )
            sections.append(
                {
                    "id": section_id,
                    "project_id": project["id"],
                    "name": name,
                }
            )

    bulk_insert(
        conn,
        table="sections",
        columns=["id", "project_id", "name", "sort_order", "created_at"],
        rows=rows,
    )

    return sections


