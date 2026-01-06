"""
Comment generator.

Adds short, conversational comments to a subset of tasks to simulate async
collaboration patterns.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from faker import Faker

from ..utils.config import VOLUME_CONFIG
from ..utils.dates import random_datetime_between
from ..utils.db import bulk_insert
from ..utils.text import generate_comment


def generate_comments(
    conn,
    tasks: List[Dict[str, str]],
    users: List[Dict[str, str]],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Attach comments to ~20% of tasks, 1–5 comments per task.
    """
    faker = faker or Faker("en_US")

    if not tasks:
        return []

    commented_fraction = VOLUME_CONFIG.commented_task_fraction
    num_tasks_with_comments = int(len(tasks) * commented_fraction)
    tasks_with_comments = random.sample(tasks, k=max(1, num_tasks_with_comments))

    rows = []
    comments: List[Dict[str, str]] = []

    for task in tasks_with_comments:
        created_at = datetime.fromisoformat(task["created_at"])
        end = (
            datetime.fromisoformat(task["completed_at"])
            if task["completed_at"]
            else datetime.utcnow()
        )

        comment_count = random.randint(1, 5)
        last_comment_time = created_at

        for _ in range(comment_count):
            comment_id = str(uuid.uuid4())
            author = random.choice(users)
            ts = random_datetime_between(last_comment_time, end)
            last_comment_time = ts

            body = generate_comment(faker)

            rows.append(
                (
                    comment_id,
                    task["id"],
                    None,  # subtask_id
                    author["id"],
                    body,
                    ts.isoformat(),
                )
            )
            comments.append(
                {
                    "id": comment_id,
                    "task_id": task["id"],
                }
            )

        # Update last_activity_at on the task to reflect most recent comment.
        conn.execute(
            "UPDATE tasks SET last_activity_at = MAX(last_activity_at, ?) WHERE id = ?",
            (last_comment_time.isoformat(), task["id"]),
        )

    bulk_insert(
        conn,
        table="comments",
        columns=["id", "task_id", "subtask_id", "author_id", "body", "created_at"],
        rows=rows,
    )

    return comments


