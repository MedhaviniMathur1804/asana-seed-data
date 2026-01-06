# """
# User generator.

# We create thousands of employees with realistic role mix, locations, and join
# dates skewed toward recent hires, reflecting ongoing growth.
# """

# from __future__ import annotations

# import random
# import uuid
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional

# from faker import Faker

# from ..utils.config import ORG_CONFIG, VOLUME_CONFIG
# from ..utils.db import bulk_insert


# def _sample_join_date() -> datetime:
#     """
#     Sample a join date within the last ~3 years, skewed toward recent months.

#     Beta(2,5) concentrates probability near 0; mapping 0->recent, 1->3 years ago.
#     """
#     span_days = 365 * 3
#     fraction = random.betavariate(2, 5)
#     days_ago = int(fraction * span_days)
#     return datetime.utcnow() - timedelta(days=days_ago)


# def _pick_role() -> str:
#     """
#     Non-uniform role distribution reflecting a product-led enterprise.
#     """
#     roles = [
#         ("Software Engineer", 0.22),
#         ("Senior Software Engineer", 0.13),
#         ("Staff Engineer", 0.04),
#         ("Product Manager", 0.07),
#         ("Product Owner", 0.03),
#         ("Product Designer", 0.07),
#         ("Design Lead", 0.02),
#         ("Data Scientist", 0.06),
#         ("Data Analyst", 0.04),
#         ("Sales Executive", 0.06),
#         ("Account Manager", 0.05),
#         ("Customer Success Manager", 0.04),
#         ("Sales Engineer", 0.03),
#         ("QA Engineer", 0.04),
#         ("IT Support Specialist", 0.03),
#         ("Security Engineer", 0.02),
#         ("Finance Analyst", 0.02),
#         ("People Ops Specialist", 0.02),
#     ]
#     labels, weights = zip(*roles)
#     return random.choices(labels, weights=weights, k=1)[0]


# def _pick_location() -> str:
#     """
#     Weighted office/remote mix to resemble distributed teams.
#     """
#     locations = [
#         ("New York", 0.18),
#         ("San Francisco", 0.15),
#         ("Austin", 0.10),
#         ("London", 0.12),
#         ("Dublin", 0.08),
#         ("Toronto", 0.07),
#         ("Bangalore", 0.10),
#         ("Remote - US", 0.12),
#         ("Remote - EMEA", 0.05),
#         ("Remote - APAC", 0.03),
#     ]
#     labels, weights = zip(*locations)
#     return random.choices(labels, weights=weights, k=1)[0]


# def generate_users(
#     conn,
#     organization: Dict[str, str],
#     faker: Optional[Faker] = None,
# ) -> List[Dict[str, str]]:
#     """
#     Generate 3k–8k users with realistic roles and join dates.

#     Headcount target uses a triangular distribution with mode leaning toward the
#     upper half to emulate continued growth.
#     """
#     faker = faker or Faker("en_US")

#     min_u, max_u = VOLUME_CONFIG.min_users, VOLUME_CONFIG.max_users
#     mode = (min_u + max_u) / 2 + 800  # bias slightly above the midpoint
#     total_users = int(round(random.triangular(min_u, max_u, mode)))
#     total_users = max(min_u, min(max_u, total_users))

#     email_counts = {}
#     rows = []
#     users: List[Dict[str, str]] = []

#     for _ in range(total_users):
#         full_name = faker.name()
#         first, last = full_name.split(" ")[0], full_name.split(" ")[-1]
#         base_email = f"{first}.{last}".replace("'", "").replace(" ", "").lower()
#         count = email_counts.get(base_email, 0)
#         email_counts[base_email] = count + 1
#         email_local = base_email if count == 0 else f"{base_email}{count}"
#         email = f"{email_local}@{ORG_CONFIG.domain}"

#         role = _pick_role()
#         location = _pick_location()
#         joined_at = _sample_join_date()
#         is_active = 1 if random.random() > 0.03 else 0  # small inactive fraction

#         user_id = str(uuid.uuid4())
#         rows.append(
#             (
#                 user_id,
#                 organization["id"],
#                 full_name,
#                 email,
#                 role,
#                 location,
#                 joined_at.isoformat(),
#                 is_active,
#                 joined_at.isoformat(),
#             )
#         )
#         users.append(
#             {
#                 "id": user_id,
#                 "role": role,
#                 "location": location,
#             }
#         )

#     bulk_insert(
#         conn,
#         table="users",
#         columns=[
#             "id",
#             "organization_id",
#             "full_name",
#             "email",
#             "role",
#             "location",
#             "joined_at",
#             "is_active",
#             "created_at",
#         ],
#         rows=rows,
#     )

#     return users


"""
User generator.

We create thousands of employees with realistic role mix, locations, and join
dates skewed toward recent hires, reflecting ongoing growth.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from faker import Faker

from ..utils.config import ORG_CONFIG, VOLUME_CONFIG
from ..utils.db import bulk_insert


def _sample_join_date() -> datetime:
    """
    Sample a join date within the last ~3 years, skewed toward recent months.

    Beta(2,5) concentrates probability near 0; mapping 0->recent, 1->3 years ago.
    """
    span_days = 365 * 3
    fraction = random.betavariate(2, 5)
    days_ago = int(fraction * span_days)
    return datetime.utcnow() - timedelta(days=days_ago)


def _pick_role() -> str:
    """
    Non-uniform role distribution reflecting a product-led enterprise.
    """
    roles = [
        ("Software Engineer", 0.22),
        ("Senior Software Engineer", 0.13),
        ("Staff Engineer", 0.04),
        ("Product Manager", 0.07),
        ("Product Owner", 0.03),
        ("Product Designer", 0.07),
        ("Design Lead", 0.02),
        ("Data Scientist", 0.06),
        ("Data Analyst", 0.04),
        ("Sales Executive", 0.06),
        ("Account Manager", 0.05),
        ("Customer Success Manager", 0.04),
        ("Sales Engineer", 0.03),
        ("QA Engineer", 0.04),
        ("IT Support Specialist", 0.03),
        ("Security Engineer", 0.02),
        ("Finance Analyst", 0.02),
        ("People Ops Specialist", 0.02),
    ]
    labels, weights = zip(*roles)
    return random.choices(labels, weights=weights, k=1)[0]


def _pick_location() -> str:
    """
    Weighted office/remote mix to resemble distributed teams.
    """
    locations = [
        ("New York", 0.18),
        ("San Francisco", 0.15),
        ("Austin", 0.10),
        ("London", 0.12),
        ("Dublin", 0.08),
        ("Toronto", 0.07),
        ("Bangalore", 0.10),
        ("Remote - US", 0.12),
        ("Remote - EMEA", 0.05),
        ("Remote - APAC", 0.03),
    ]
    labels, weights = zip(*locations)
    return random.choices(labels, weights=weights, k=1)[0]


def generate_users(
    conn,
    organization: Dict[str, str],
    faker: Optional[Faker] = None,
) -> List[Dict[str, str]]:
    """
    Generate 3k–8k users with realistic roles and join dates.

    Headcount target uses a triangular distribution with mode leaning toward the
    upper half to emulate continued growth.
    """
    faker = faker or Faker("en_US")

    min_u, max_u = VOLUME_CONFIG.min_users, VOLUME_CONFIG.max_users
    mode = (min_u + max_u) / 2 + 800
    total_users = int(round(random.triangular(min_u, max_u, mode)))
    total_users = max(min_u, min(max_u, total_users))

    used_emails = set()
    rows = []
    users: List[Dict[str, str]] = []

    for _ in range(total_users):
        full_name = faker.name()
        first = full_name.split(" ")[0]
        last = full_name.split(" ")[-1]

        # base_email = (
        #     f"{first}.{last}"
        #     .replace("'", "")
        #     .replace(" ", "")
        #     .lower()
        # )

        # # Ensure UNIQUE emails (required by schema)
        # email = f"{base_email}@{ORG_CONFIG.domain}"
        # counter = 1
        # while email in used_emails:
        #     email = f"{base_email}{counter}@{ORG_CONFIG.domain}"
        #     counter += 1
        # used_emails.add(email)
       

        role = _pick_role()
        location = _pick_location()
        joined_at = _sample_join_date()
        is_active = 1 if random.random() > 0.03 else 0  # small inactive fraction

        user_id = str(uuid.uuid4())
        email = f"user-{uuid.uuid4().hex[:8]}@{ORG_CONFIG.domain}"
        rows.append(
            (
                user_id,
                organization["id"],
                full_name,
                email,
                role,
                location,
                joined_at.isoformat(),
                is_active,
                joined_at.isoformat(),
            )
        )

        users.append(
            {
                "id": user_id,
                "role": role,
                "location": location,
            }
        )

    bulk_insert(
        conn,
        table="users",
        columns=[
            "id",
            "organization_id",
            "full_name",
            "email",
            "role",
            "location",
            "joined_at",
            "is_active",
            "created_at",
        ],
        rows=rows,
    )

    return users
