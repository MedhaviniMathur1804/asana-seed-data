"""
Configuration values for the Asana-like data generator.

All numeric volumes and distribution weights live here so that:
- Experiments can tweak scale without touching generator logic.
- Downstream users can see expected dataset sizes in one place.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OrgConfig:
    name: str = "Acme Global Solutions"
    domain: str = "acme-corp.com"


@dataclass(frozen=True)
class VolumeConfig:
    # User base for a large enterprise deployment
    min_users: int = 3000
    max_users: int = 8000

    # Teams per organization
    min_teams: int = 8
    max_teams: int = 15

    # Projects per team
    min_projects_per_team: int = 3
    max_projects_per_team: int = 10

    # Tasks per project
    min_tasks_per_project: int = 40
    max_tasks_per_project: int = 120

    # Subtasks: fraction of tasks that have subtasks
    min_subtask_task_fraction: float = 0.30
    max_subtask_task_fraction: float = 0.40

    # Comments: fraction of tasks that have comments
    commented_task_fraction: float = 0.20


@dataclass(frozen=True)
class TaskConfig:
    # Target completion ratio for tasks
    completion_ratio: float = 0.65

    # Probability that a task is unassigned; real orgs often have some backlog unassigned
    unassigned_task_probability: float = 0.20

    # Probability that a task is overdue (past due_date and not completed)
    overdue_task_probability: float = 0.10


@dataclass(frozen=True)
class DBConfig:
    # Relative path for the SQLite file produced by the generator
    output_path: str = "asana-seed-data/output/asana_simulation.sqlite"
    schema_path: str = "asana-seed-data/schema.sql"


ORG_CONFIG = OrgConfig()
VOLUME_CONFIG = VolumeConfig()
TASK_CONFIG = TaskConfig()
DB_CONFIG = DBConfig()


