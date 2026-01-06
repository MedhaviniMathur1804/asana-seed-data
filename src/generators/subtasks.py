"""
Subtask generator.

Adds hierarchical structure beneath a subset of tasks, with completion
correlated to the parent task’s status.
"""

# from __future__ import annotations

# import random
# import uuid
# from datetime import datetime
# from typing import Dict, List, Optional

# from faker import Faker

# from ..utils.config import VOLUME_CONFIG
# from ..utils.dates import business_due_date_from_created, completed_after_created, random_datetime_between
# from ..utils.db import bulk_insert
# from ..utils.text import generate_subtask_title


# def generate_subtasks(
#     conn,
#     organization_id: str,
#     tasks: List[Dict[str, str]],
#     faker: Optional[Faker] = None,
# ) -> List[Dict[str, str]]:
#     """
#     Generate subtasks for 30–40% of tasks, 2–6 subtasks each.
#     """
#     faker = faker or Faker("en_US")

#     if not tasks:
#         return []

#     min_frac = VOLUME_CONFIG.min_subtask_task_fraction
#     max_frac = VOLUME_CONFIG.max_subtask_task_fraction
#     target_frac = random.uniform(min_frac, max_frac)
#     num_parents = int(len(tasks) * target_frac)
#     parent_tasks = random.sample(tasks, k=max(1, num_parents))

#     subtasks: List[Dict[str, str]] = []
#     rows = []
#     now = datetime.utcnow()

#     for parent in parent_tasks:
#         parent_created = datetime.fromisoformat(parent["created_at"])
#         parent_completed = (
#             datetime.fromisoformat(parent["completed_at"]) if parent["completed_at"] else None
#         )
#         parent_due = (
#             datetime.fromisoformat(parent["due_date"]).date() if parent["due_date"] else None
#         )

#         count = random.randint(2, 6)
#         base_sort = 0

#         for i in range(count):
#             sub_id = str(uuid.uuid4())
#             created_at = random_datetime_between(parent_created, parent_completed or now)

#             # Subtasks often share the parent due date or slightly earlier.
#             if parent_due and random.random() < 0.8:
#                 due_date = parent_due
#             else:
#                 due_date = business_due_date_from_created(created_at, min_days=1, max_days=30)

#             # Correlate completion with parent: if parent done, most subtasks done.
#             if parent_completed:
#                 completed_prob = 0.9
#             else:
#                 completed_prob = 0.3
#             completed_at = None
#             if random.random() < completed_prob:
#                 completed_at = completed_after_created(created_at, due_date, min_hours=1, max_days=30)

#             assignee_id = parent["assignee_id"]
#             # Occasionally delegate subtasks to others to mimic collaboration.
#             if assignee_id and random.random() < 0.15:
#                 assignee_id = None

#             title = generate_subtask_title(parent_title="(hidden)")
#             # We don’t need the full parent title for training; we just want structure.

#             rows.append(
#                 (
#                     sub_id,
#                     parent["id"],
#                     parent["project_id"],
#                     organization_id,
#                     title,
#                     None,
#                     assignee_id,
#                     assignee_id,  # created_by: usually whoever owns the parent
#                     created_at.isoformat(),
#                     due_date.isoformat() if due_date else None,
#                     completed_at.isoformat() if completed_at else None,
#                     base_sort + i,
#                 )
#             )
#             subtasks.append(
#                 {
#                     "id": sub_id,
#                     "parent_task_id": parent["id"],
#                     "project_id": parent["project_id"],
#                 }
#             )

#     bulk_insert(
#         conn,
#         table="subtasks",
#         columns=[
#             "id",
#             "parent_task_id",
#             "project_id",
#             "organization_id",
#             "name",
#             "description",
#             "assignee_id",
#             "created_by_user_id",
#             "created_at",
#             "due_date",
#             "completed_at",
#             "sort_order",
#         ],
#         rows=rows,
#     )

#     return subtasks


from __future__ import annotations

import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from faker import Faker

from ..utils.config import VOLUME_CONFIG
from ..utils.dates import (
    business_due_date_from_created,
    completed_after_created,
    random_datetime_between,
)
from ..utils.db import bulk_insert
from ..utils.text import generate_subtask_title


def generate_subtasks(
    conn,
    organization_id: str,
    tasks: List[Dict[str, str]],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Generate subtasks for 30–40% of tasks, 2–6 subtasks each.
    Ensures every subtask has a creator (created_by_user_id).
    """
    faker = faker or Faker("en_US")

    if not tasks:
        return []

    min_frac = VOLUME_CONFIG.min_subtask_task_fraction
    max_frac = VOLUME_CONFIG.max_subtask_task_fraction
    target_frac = random.uniform(min_frac, max_frac)
    num_parents = int(len(tasks) * target_frac)
    parent_tasks = random.sample(tasks, k=max(1, num_parents))

    subtasks: List[Dict[str, str]] = []
    rows = []
    now = datetime.utcnow()

    # Collect possible creators from tasks (any assigned user)
    possible_creators = [
        t["assignee_id"] for t in tasks if t.get("assignee_id")
    ]

    for parent in parent_tasks:
        parent_created = datetime.fromisoformat(parent["created_at"])
        parent_completed = (
            datetime.fromisoformat(parent["completed_at"])
            if parent["completed_at"]
            else None
        )
        parent_due = (
            datetime.fromisoformat(parent["due_date"]).date()
            if parent["due_date"]
            else None
        )

        count = random.randint(2, 6)
        base_sort = 0

        for i in range(count):
            sub_id = str(uuid.uuid4())
            created_at = random_datetime_between(
                parent_created, parent_completed or now
            )

            # Subtasks often share the parent due date or slightly earlier.
            if parent_due and random.random() < 0.8:
                due_date = parent_due
            else:
                due_date = business_due_date_from_created(
                    created_at, min_days=1, max_days=30
                )

            # Correlate completion with parent completion.
            completed_at = None
            if parent_completed:
                if random.random() < 0.9:
                    completed_at = completed_after_created(
                        created_at, due_date, min_hours=1, max_days=30
                    )
            else:
                if random.random() < 0.3:
                    completed_at = completed_after_created(
                        created_at, due_date, min_hours=1, max_days=30
                    )

            # Creator: always required
            if parent.get("assignee_id"):
                created_by_user_id = parent["assignee_id"]
            else:
                created_by_user_id = random.choice(possible_creators)

            # Assignee: may be None to mimic delegation
            assignee_id = parent.get("assignee_id")
            if assignee_id and random.random() < 0.15:
                assignee_id = None

            title = generate_subtask_title(parent_title="(hidden)")

            rows.append(
                (
                    sub_id,
                    parent["id"],
                    parent["project_id"],
                    organization_id,
                    title,
                    None,
                    assignee_id,
                    created_by_user_id,
                    created_at.isoformat(),
                    due_date.isoformat() if due_date else None,
                    completed_at.isoformat() if completed_at else None,
                    base_sort + i,
                )
            )

            subtasks.append(
                {
                    "id": sub_id,
                    "parent_task_id": parent["id"],
                    "project_id": parent["project_id"],
                }
            )

    bulk_insert(
        conn,
        table="subtasks",
        columns=[
            "id",
            "parent_task_id",
            "project_id",
            "organization_id",
            "name",
            "description",
            "assignee_id",
            "created_by_user_id",
            "created_at",
            "due_date",
            "completed_at",
            "sort_order",
        ],
        rows=rows,
    )

    return subtasks
