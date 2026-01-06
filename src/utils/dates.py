"""
Date/time helpers focused on realistic project/task lifecycles.

Key goals:
- Bias events toward recent history (active work).
- Prefer business days for due dates.
- Ensure temporal consistency between created/due/completed timestamps.
"""

from __future__ import annotations

import calendar
import random
from datetime import date, datetime, timedelta


def random_datetime_between(start: datetime, end: datetime) -> datetime:
    """
    Sample a datetime between start and end, skewed toward end (more recent).

    We use a Beta(2, 5) distribution over the interval, which concentrates
    probability near 0 -> mapped to dates close to `end`.
    """
    if start >= end:
        return start
    total_seconds = (end - start).total_seconds()
    frac = random.betavariate(2, 5)
    offset = total_seconds * (1 - frac)
    return start + timedelta(seconds=offset)


def _to_business_day(d: date) -> date:
    """
    Snap a date to the closest weekday.

    We nudge weekend due dates to Friday or Monday to resemble real scheduling.
    """
    weekday = d.weekday()
    if weekday < 5:
        return d
    # Saturday (5) -> Friday or Monday; Sunday (6) -> Monday
    if weekday == 5:
        return d - timedelta(days=1) if random.random() < 0.6 else d + timedelta(days=2)
    return d + timedelta(days=1)


def business_due_date_from_created(
    created_at: datetime,
    min_days: int = 1,
    max_days: int = 90,
) -> date:
    """
    Generate a due date after creation, preferring 1–4 week horizons.

    We use a triangular distribution with a mode at ~21 days, then snap to a
    business day to avoid clustering on weekends.
    """
    if max_days <= 0:
        return _to_business_day(created_at.date())
    mode = min_days + (max_days - min_days) * 0.35
    offset_days = int(round(random.triangular(min_days, max_days, mode)))
    offset_days = max(min_days, min(max_days, offset_days))
    raw_date = created_at.date() + timedelta(days=offset_days)
    return _to_business_day(raw_date)


def completed_after_created(
    created_at: datetime,
    due: date | None,
    min_hours: int = 1,
    max_days: int = 60,
) -> datetime:
    """
    Generate a completion timestamp after creation, loosely influenced by due date.

    - If a due date exists, we bias completion to occur before or shortly after it.
    - Otherwise, we keep completion within a configurable window after creation.
    """
    earliest = created_at + timedelta(hours=min_hours)
    latest = created_at + timedelta(days=max_days)

    if due is not None:
        due_dt = datetime.combine(due, datetime.min.time())
        # Allow completion from a bit before due to a bit after.
        earliest = min(earliest, due_dt - timedelta(days=7))
        latest = min(latest, due_dt + timedelta(days=14))

    if earliest >= latest:
        return earliest
    return random_datetime_between(earliest, latest)


def is_overdue(due: date | None, completed_at: datetime | None, now: datetime | None = None) -> bool:
    """
    Determine whether an item is overdue: due date in the past and not completed.
    """
    if due is None:
        return False
    now = now or datetime.utcnow()
    if completed_at is not None:
        return False
    return due < now.date()


