"""
Entry point for generating the Asana-like simulation dataset.

Orchestration only: all generation logic lives in dedicated modules.
"""

from __future__ import annotations

from faker import Faker

# from utils.db import apply_schema, db_session
# from generators.organizations import generate_organization
# from generators.teams import generate_teams
# from generators.users import generate_users
# from generators.team_memberships import generate_team_memberships
# from generators.projects import generate_projects
# from generators.sections import generate_sections
# from generators.tasks import generate_tasks
# from generators.subtasks import generate_subtasks
# from generators.comments import generate_comments

from src.utils.db import apply_schema, db_session
from src.generators.organizations import generate_organization
from src.generators.teams import generate_teams
from src.generators.users import generate_users
from src.generators.team_memberships import generate_team_memberships
from src.generators.projects import generate_projects
from src.generators.sections import generate_sections
from src.generators.tasks import generate_tasks
from src.generators.subtasks import generate_subtasks
from src.generators.comments import generate_comments



def run() -> None:
    """
    Build the SQLite dataset in dependency order:
    1) organization -> 2) teams -> 3) users -> 4) team memberships
    5) projects -> 6) sections -> 7) tasks -> 8) subtasks -> 9) comments

    Each step passes IDs forward to preserve referential integrity.
    """
    faker = Faker("en_US")

    with db_session() as conn:
        apply_schema(conn)

        org = generate_organization(conn, faker=faker)
        teams = generate_teams(conn, organization=org, faker=faker)
        users = generate_users(conn, organization=org, faker=faker)
        memberships = generate_team_memberships(conn, teams=teams, users=users, faker=faker)
        projects = generate_projects(conn, organization_id=org["id"], teams=teams, faker=faker)
        sections = generate_sections(conn, projects=projects, faker=faker)
        tasks = generate_tasks(
            conn,
            organization_id=org["id"],
            projects=projects,
            sections=sections,
            users=users,
            memberships=memberships,
            faker=faker,
        )
        subtasks = generate_subtasks(
            conn,
            organization_id=org["id"],
            tasks=tasks,
            faker=faker,
        )
        generate_comments(
            conn,
            tasks=tasks,
            users=users,
            faker=faker,
        )


if __name__ == "__main__":
    run()


