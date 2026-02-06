# Claude Code Instructions for Brief

This file contains conventions and guidelines for Claude Code working on the Brief project — an AI-powered personalized content curation agent.

## Project Overview

Brief is a system that ingests content from curated sources, normalizes and enriches it, then produces a daily digest organized into three lanes: **Builders** (cutting-edge AI projects, agents, tools), **Security** (AI safety, threat modeling, failure modes), and **Business** (enterprise AI implementations, ROI, strategy).

## Git Workflow

### Commit Message Convention

All commit messages should follow this pattern:

```
v{MAJOR}.{MINOR}.{SUB}/{CATEGORY}: {Description}

{Extended description if needed}

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Format:**
- `{MAJOR}.{MINOR}` — The milestone (e.g., `0.1` maps to `milestones/*/v0.1/`)
- `{SUB}` — The spec number (e.g., `001` maps to file `001-feature-name.md`)
- `{CATEGORY}` — The type of change (see below)

**Category Types:**
- **feature** - New functionality
- **refactor** - Code reorganization or restructuring
- **bugfix** - Bug fixes
- **docs** - Documentation updates
- **test** - Test additions or improvements
- **chore** - Maintenance, dependencies, build config

## Development Principles

### Graceful Degradation Over Fail Fast

- When something is missing or optional, provide sensible defaults and keep the system working
- Only error out if something truly essential breaks
- Handle the happy path cleanly, add error handling only for real observed problems

### Minimal & Functional

- Only implement what's needed for the current milestone
- Don't add features planned for future milestones unless necessary
- Remove unused code promptly
- Never add code "just in case we might need it"

### No Over-Engineering

- Don't add error handling, fallbacks, or validation for scenarios that can't happen
- Don't create helpers, utilities, or abstractions for one-time operations
- Three similar lines of code is better than a premature abstraction
- Don't design for hypothetical future requirements

## Documentation Standards

### Sensitive Information

**CRITICAL**: Never include actual credentials, API keys, or environment secrets in milestone documents or any committed files.

- Use placeholder examples: `your-api-key-here`
- Provide instructions for where to get values
- Milestone documents are checked into git — secrets in commit history are permanent

## Notes for Claude Code Sessions

### Before Starting Work
- Check `milestones/active/` for current work in progress
- If unsure which milestone to work on, **ASK** before starting
- Read `milestones/claude.md` for documentation workflow

### During Development
- Test changes before presenting them to the user
- Keep commits focused (one logical change per commit)
- Update documentation immediately if spec doesn't match reality

### After Completing Work

**IMPORTANT: Do NOT automatically commit and push**

- Verify the work is complete and functional
- **STOP AND WAIT** — Do not touch git yet
- Wait for user to test and validate the changes
- Only commit and push when user explicitly requests it

---

*Last Updated: February 5, 2026*
