# Brief Project Milestones

## WHAT / TO WHOM / WHY

**WHAT**: A structured milestone system that defines project capabilities, requirements, and success criteria for building the Brief AI content curation agent.

**TO WHOM**: The project owner and any AI assistants working on the project.

**WHY**: Provides clear project scope, enables accurate progress tracking, and ensures every piece of work ties back to a concrete deliverable.

---

## Folder Structure

```
milestones/
├── claude.md                    # This file - instructions for milestone docs
├── active/                      # Currently in development (1-4 items)
│   └── v0.1/
│       ├── README.md            # Milestone overview, status, requirements
│       ├── 001-feature-a.md     # Spec (commit as v0.1.001)
│       └── 002-feature-b.md     # Spec (commit as v0.1.002)
│
├── backlog/                     # Upcoming work with documented requirements
│   └── v0.2/
│       └── README.md
│
└── done/                        # Completed milestones
    └── v0.1/
        └── ...
```

### Versioning Scheme

- **Milestone folders**: `v{MAJOR}.{MINOR}/` (e.g., `v0.1/`)
- **Spec files**: `{SUB}-feature-name.md` (e.g., `001-ingestion-pipeline.md`)
- **Commit messages**: `v{MAJOR}.{MINOR}.{SUB}` (e.g., `v0.1.001`)

### Status Folders

| Folder | Description |
|--------|-------------|
| `active/` | Currently being built (1-4 items) |
| `backlog/` | Planned, specs optional until work begins |
| `done/` | Completed work |

**Workflow:**
1. Create a milestone folder in `backlog/` with a README listing planned specs
2. Create detailed spec files as work begins
3. Move to `active/` when development begins
4. Move the **entire milestone folder** to `done/` when **all specs are shipped**

**Never move individual spec files.** Specs stay inside their milestone folder. Mark status as DONE within the file, but leave it in place.

## Spec Format

### NO CODE IN MILESTONE DOCUMENTS

Milestone documents focus on WHAT and WHY, not HOW.

**Instead of code examples**:
- Use clear behavioral descriptions
- Define input/output contracts
- Specify acceptance criteria
- Describe expected outcomes

### Required Sections

All specs MUST include:

**WHAT / TO WHOM / WHY**
- **WHAT**: Clear description of what capability is being built
- **TO WHOM**: Who benefits from this capability
- **WHY**: The business value or problem this solves

**Requirements**: Behavioral requirements (not implementation details)

**Success Criteria**: Measurable, testable outcomes

### Status Values (in order)

1. `IN REFINEMENT` — Draft exists but needs review. **All first drafts start here.**
2. `READY TO START` — Reviewed, approved, and ready for implementation.
3. `IN PROGRESS` — Active development is happening.
4. `IN TESTING` — Implementation complete, being validated.
5. `DONE` — Shipped and verified.

### Templates

**Milestone README.md:**

```markdown
# v0.X: [Milestone Name]

**Status**: IN REFINEMENT | READY TO START | IN PROGRESS | DONE

## WHAT / TO WHOM / WHY

**WHAT**: [Clear description of what capability is being built]
**TO WHOM**: [Who benefits]
**WHY**: [Business value or problem this solves]

## Requirements

[Clear behavioral requirements without code]

## Success Criteria

[Measurable outcomes and acceptance criteria]

## Specs

- [ ] 001: [Feature name]
- [ ] 002: [Feature name]
```

**Spec file (XXX-feature-name.md):**

```markdown
# [Feature Name] -- **STATUS**

## WHAT / TO WHOM / WHY

**WHAT**: [Specific capability being built]
**TO WHOM**: [Who benefits]
**WHY**: [Business value]

## Requirements

[Behavioral requirements for this specific feature]

## Success Criteria

- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
```

---

**Remember**: Milestone documents define WHAT and WHY, not HOW. Implementation details belong in code, not specs.
