-- Asana-like simulation schema for a single large enterprise
-- Design goals:
-- - Mirror real-world Asana usage patterns
-- - Favor normalization for clarity and easier reasoning by AI agents
-- - Use UUIDs (TEXT) as primary keys to resemble API IDs
-- - Capture lifecycle timestamps (created_at, completed_at, due_date, last_activity_at)
-- - Enforce referential integrity using foreign keys

PRAGMA foreign_keys = ON;

-- ORGANIZATIONS
-- A single large company using Asana. Kept generic so we can extend to multi-org later.
CREATE TABLE IF NOT EXISTS organizations (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT,              -- e.g., company.com
    created_at      DATETIME NOT NULL
);

-- TEAMS
-- Functional groups (Engineering, Design, Marketing, etc.) within the organization.
CREATE TABLE IF NOT EXISTS teams (
    id              TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- USERS
-- Employees with roles and join dates. Users can belong to multiple teams.
CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    role            TEXT NOT NULL,     -- e.g., "Engineer", "Manager", "Designer"
    location        TEXT,              -- rough office/region
    joined_at       DATETIME NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- TEAM MEMBERSHIPS
-- Many-to-many mapping between users and teams.
CREATE TABLE IF NOT EXISTS team_memberships (
    id         TEXT PRIMARY KEY,
    team_id    TEXT NOT NULL,
    user_id    TEXT NOT NULL,
    role       TEXT,                   -- e.g., "member", "lead"
    added_at   DATETIME NOT NULL,
    UNIQUE (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- PROJECTS
-- Collections of tasks within a team (roadmap, sprint, launch, ops, etc.).
CREATE TABLE IF NOT EXISTS projects (
    id              TEXT PRIMARY KEY,
    team_id         TEXT NOT NULL,
    organization_id TEXT NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    project_type    TEXT NOT NULL,     -- "roadmap", "sprint", "launch", "ops", etc.
    start_date      DATE,
    due_date        DATE,
    created_at      DATETIME NOT NULL,
    completed_at    DATETIME,          -- populated for fully completed projects
    is_archived     INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- SECTIONS
-- Kanban-like columns or workflow stages within a project.
CREATE TABLE IF NOT EXISTS sections (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL,
    name        TEXT NOT NULL,        -- e.g., "Backlog", "In Progress"
    sort_order  INTEGER NOT NULL,     -- to preserve board order
    created_at  DATETIME NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- TASKS
-- Top-level tasks within a project. Tasks can optionally belong to a section and have an assignee.
CREATE TABLE IF NOT EXISTS tasks (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT NOT NULL,
    section_id          TEXT,                 -- nullable: tasks may be unsectioned
    organization_id     TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,
    assignee_id         TEXT,                -- nullable: tasks may be unassigned
    created_by_user_id  TEXT NOT NULL,       -- who created the task
    created_at          DATETIME NOT NULL,
    due_date            DATE,
    completed_at        DATETIME,
    last_activity_at    DATETIME NOT NULL,   -- updated when comments/subtasks complete, etc.
    priority            TEXT,                -- e.g., "low", "medium", "high", "urgent"
    is_deleted          INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- SUBTASKS
-- Task items that belong to a parent task. Modeled separately rather than self-referencing
-- to make downstream reasoning simpler for agents while still capturing hierarchy.
CREATE TABLE IF NOT EXISTS subtasks (
    id                  TEXT PRIMARY KEY,
    parent_task_id      TEXT NOT NULL,
    project_id          TEXT NOT NULL,        -- denormalized for easier querying
    organization_id     TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,
    assignee_id         TEXT,
    created_by_user_id  TEXT NOT NULL,
    created_at          DATETIME NOT NULL,
    due_date            DATE,
    completed_at        DATETIME,
    sort_order          INTEGER NOT NULL,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- COMMENTS
-- Short conversational messages attached to either tasks or subtasks. Represented as a single
-- table with nullable foreign key to subtask; one of (task_id, subtask_id) must be non-null.
CREATE TABLE IF NOT EXISTS comments (
    id              TEXT PRIMARY KEY,
    task_id         TEXT,                -- nullable if comment is on a subtask
    subtask_id      TEXT,                -- nullable if comment is on a task
    author_id       TEXT NOT NULL,
    body            TEXT NOT NULL,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (subtask_id) REFERENCES subtasks(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes chosen to mirror common query patterns in Asana-like tools.

-- Users often filter by team/project and completion state.
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_completed_at ON tasks(completed_at);

-- Subtasks commonly accessed via parent.
CREATE INDEX IF NOT EXISTS idx_subtasks_parent ON subtasks(parent_task_id);

-- Comments frequently queried by task/subtask.
CREATE INDEX IF NOT EXISTS idx_comments_task ON comments(task_id);
CREATE INDEX IF NOT EXISTS idx_comments_subtask ON comments(subtask_id);


