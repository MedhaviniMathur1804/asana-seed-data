## Asana-Like Seed Data Generator

This project generates a realistic SQLite database that simulates how a large enterprise uses an Asana-like work management tool. The focus is on data realism, relational integrity, and reproducibility so computer-use AI agents can be evaluated against production-like task management data without relying on external services.

---

## Project Overview

- Purpose: Produce a rich, enterprise-scale Asana-style dataset that reflects real work patterns (cross-functional teams, staged workflows, partial completion, overdue items, sparse comments).
- Why realism matters: AI agents need data that mirrors actual operational noise—unassigned tasks, uneven completion rates, staggered creation times, and varied project types—to make evaluation meaningful.

---

## Scope and Alignment

Implemented entities (all defined in `schema.sql` and generated under `src/generators/`):
- Organizations, Teams, Users, Team Memberships
- Projects, Sections
- Tasks, Subtasks
- Comments

---

## Out of Scope (Intentionally Omitted)

- Custom Fields, Tags, Attachments, external APIs: excluded to keep the core relational model focused and reproducible without external dependencies. The current scope concentrates on canonical Asana-like primitives needed for task management workflows.

---

## Data Realism Methodology

- **Non-uniform task completion**: Only ~60–70% of tasks are completed; the rest remain in-flight or not started to mirror real backlogs.
- **Overdue and unassigned tasks**: A controlled fraction of due-dated tasks are overdue; some tasks intentionally lack assignees to reflect grooming gaps.
- **Temporal consistency**: `created_at`, `due_date`, and `completed_at` follow logical ordering; completion is always after creation and typically near due dates; due dates are snapped to business days.
- **Sparse comments**: Only ~20% of tasks receive 1–5 short, conversational comments to reflect async collaboration without over-saturation.

Additional realism: weighted roles/locations, role-aligned team memberships, weighted project types (roadmap/sprint/launch/ops), and staggered historical creation dates across org/team/project/user entities. Text is template-driven to avoid generic “Task 1” patterns.

---

## Dataset Scale (Configurable)

Enterprise-level magnitudes (controlled via `src/utils/config.py`):
- 8–15 teams under one organization.
- 3,000–8,000 users with weighted roles and locations.
- 3–10 projects per team with mixed types.
- 40–120 tasks per project, with 30–40% of tasks carrying subtasks.
- Comments on ~20% of tasks, 1–5 comments each.

---

## Data Model Overview

The schema uses UUID (TEXT) primary keys and foreign keys throughout. Key relationships:
- Organization → Teams, Users, Projects
- Team → Projects and Users (via Team Memberships)
- Project → Sections, Tasks
- Task → optional Section, optional Assignee; has Subtasks and Comments
- Subtask → parent Task (shares project/organization)
- Comment → Task (and structurally ready for Subtask comments)

Lifecycle fields (`created_at`, `due_date`, `completed_at`, `last_activity_at`) support temporal reasoning over tasks and subtasks.

---

## Folder Structure

- **`schema.sql`**: SQLite DDL, tables, indexes, foreign keys.
- **`requirements.txt`**: Dependencies (standard library + Faker).
- **`src/`**: Python source.
  - `src/main.py`: Orchestration entry point.
  - `src/utils/`: `db.py`, `dates.py`, `text.py`, `config.py`.
  - `src/generators/`: organizations, teams, users, team_memberships, projects, sections, tasks, subtasks, comments.
- **`output/`**: Generated SQLite file lives here (`asana_simulation.sqlite`).

---

## How to Run

1) Optional virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

2) Install dependencies:
```bash
pip install -r requirements.txt
```

3) Generate the dataset from the project root:
```bash
python -m src.main
```
This will create or overwrite `output/asana_simulation.sqlite`, apply `schema.sql`, and run generators in dependency order (organization → teams → users → team memberships → projects → sections → tasks → subtasks → comments).

---

## Output Database

Generated file: **`output/asana_simulation.sqlite`**

Contents (config-driven):
- One organization with 8–15 teams.
- 3,000–8,000 users across teams via memberships.
- 3–10 projects per team with roadmap/sprint/launch/ops mix.
- 40–120 tasks per project with realistic completion, overdue, and unassigned proportions.
- Subtasks on ~30–40% of tasks; comments on ~20% of tasks (1–5 each).

Inspect with any SQLite-compatible tool (`sqlite3`, DB Browser for SQLite, etc.).

---

## Configuration

`src/utils/config.py` centralizes all tunable parameters: volumes (users, teams, projects, tasks), fractions for subtasks and comments, completion ratios, overdue and unassigned probabilities. Adjust values there to scale the dataset or shift behavioral patterns without touching generator code or schema.

---

## AI Usage Transparency

AI was used as a design and debugging assistant. Code and schema decisions are explicitly reviewed and implemented in the repository; no autonomous code generation pipelines are invoked at runtime.

---

## API Keys and External Integrations

No API keys, external services, or third-party integrations are required. Everything runs locally with SQLite and Faker.

---

## Validation

- Referential integrity is enforced via SQLite foreign keys (enabled at connection time) and generator ordering that passes IDs between steps.
- Distribution sanity: non-uniform sampling (triangular and weighted choices) is centralized in code and configurable via `config.py` to keep volumes and ratios within expected enterprise ranges. Adjustments can be verified by querying counts in the resulting SQLite file.
