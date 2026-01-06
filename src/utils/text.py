"""
Text helpers for realistic task titles, subtasks, and comments.

We rely on lightweight templates instead of pure lorem ipsum so that titles
encode intent, scope, and sometimes the workflow stage.
"""

from __future__ import annotations

import random
from typing import Optional

from faker import Faker


_VERBS = [
    "Review",
    "Implement",
    "Draft",
    "Refine",
    "Validate",
    "Align on",
    "Plan",
    "Sync on",
    "Estimate",
    "Document",
    "Prioritize",
    "Migrate",
    "Clean up",
    "Backfill",
]

_OBJECTS_PRODUCT = [
    "API contract for {area}",
    "feature spec for {area}",
    "user journey for {area}",
    "acceptance criteria for {area}",
    "tracking plan for {area}",
]

_OBJECTS_ENGINEERING = [
    "service dependency graph",
    "background job reliability",
    "database query performance",
    "error handling for edge cases",
    "deployment pipeline",
]

_OBJECTS_GO_TO_MARKET = [
    "launch messaging",
    "sales enablement deck",
    "onboarding guide",
    "pricing one-pager",
    "FAQ document",
]

_AREAS = [
    "billing",
    "onboarding",
    "notifications",
    "workspace settings",
    "mobile experience",
    "reporting dashboards",
    "admin controls",
]


def _pick_area() -> str:
    return random.choice(_AREAS)


def generate_task_title(
    faker: Faker,
    project_type: str,
    section_name: Optional[str] = None,
) -> str:
    """
    Human-sounding task titles with light awareness of project type/section.

    We bias wording:
    - roadmap/launch work leans toward specs, messaging, and planning.
    - sprint work leans toward implementation and bug fixing.
    - ops work leans toward reliability, runbooks, and cleanups.
    """
    verb = random.choice(_VERBS)
    area = _pick_area()

    if project_type in {"roadmap", "launch"}:
        obj = random.choice(_OBJECTS_PRODUCT + _OBJECTS_GO_TO_MARKET)
    elif project_type == "sprint":
        obj = random.choice(_OBJECTS_ENGINEERING + _OBJECTS_PRODUCT)
    else:  # ops
        obj = random.choice(
            [
                "runbook for {area} incidents",
                "alert thresholds for {area}",
                "playbook for {area} handoffs",
                "cleanup tasks for {area}",
            ]
        )

    phrase = f"{verb} " + obj.format(area=area)

    if section_name and section_name.lower() in {"backlog", "ideas"} and random.random() < 0.4:
        phrase = "Candidate: " + phrase
    return phrase


def generate_subtask_title(parent_title: str) -> str:
    """
    Short, action-oriented subtask titles derived from the parent.
    """
    prefixes = [
        "Draft",
        "Review",
        "Finalize",
        "Get sign-off on",
        "Update",
        "Double-check",
        "Clarify",
    ]
    prefix = random.choice(prefixes)
    # Keep only a short suffix from parent to avoid overly long titles.
    focus = parent_title.split(" for ")[-1]
    return f"{prefix} {focus}"


_COMMENT_SNIPPETS = [
    "Let’s sync on this before EOD.",
    "Pushing this to next sprint based on priorities.",
    "Blocked until we hear back from legal.",
    "Dropping a quick note here instead of email.",
    "Can we clarify the scope in the description?",
    "Looks good to me, thanks for the update.",
    "Flagging that this might impact reporting.",
    "Happy to pair on this if helpful.",
    "Let’s keep this aligned with the roadmap doc.",
    "Moving this to In Progress now.",
]


def generate_comment(faker: Faker) -> str:
    """
    Short, conversational comment that reads like internal async communication.
    """
    if random.random() < 0.7:
        return random.choice(_COMMENT_SNIPPETS)
    # Occasionally fall back to a very short Faker sentence for variety.
    return faker.sentence(nb_words=random.randint(6, 14))


