# Schema Design Guidance

Prompt Focus:
- Identify core entities used in enterprise task management tools
- Define realistic relationships and constraints
- Enforce data integrity using foreign keys and uniqueness constraints

Author Decisions:
- Normalized schema to avoid duplication
- Enforced NOT NULL and UNIQUE constraints to surface data quality issues
- Explicit separation of tasks, subtasks, and comments

AI Role:
AI was used to sanity-check schema completeness and identify missing relationships.
Final schema structure and constraints were manually reviewed and refined.
