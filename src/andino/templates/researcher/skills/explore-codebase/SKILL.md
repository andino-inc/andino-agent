---
name: explore-codebase
description: "Systematic repository analysis — clone, explore structure, identify tech stack, map dependencies, and document patterns"
---
# Explore Codebase

## Arguments

- `$0` (required): Repository reference — GitHub URL (e.g., `https://github.com/org/repo`), org/repo format, or local path
- `focus` (optional): Specific area to focus on (e.g., "authentication", "API layer", "database models")

## Steps

1. **Get the code**
   - If GitHub URL or org/repo → clone to workspace: `gh repo clone <repo> <workspace>/<repo_name>`
   - If local path → use `file_read` directly
   - Note: `shell` requires HITL approval

2. **Explore top-level structure**
   - Run `ls -la` and `tree -L 2` to understand directory layout
   - Read README.md if it exists
   - Identify the project type from key files:
     - `package.json` → Node.js/JavaScript
     - `pyproject.toml` / `setup.py` / `requirements.txt` → Python
     - `go.mod` → Go
     - `Cargo.toml` → Rust
     - `pom.xml` / `build.gradle` → Java/Kotlin
     - `Dockerfile` / `docker-compose.yml` → containerized

3. **Identify tech stack**
   - Read the dependency file (package.json, pyproject.toml, go.mod, etc.)
   - Note: framework, ORM, test framework, linter, CI/CD tool
   - Check for infrastructure files: Terraform, Helm, CloudFormation, etc.

4. **Read entry points**
   - Find and read the main entry point (main.py, index.ts, main.go, etc.)
   - Find API routes or CLI commands
   - Understand the startup flow

5. **Map the architecture**
   - Identify the directory structure pattern (MVC, hexagonal, feature-based, etc.)
   - List the main modules/packages and their responsibilities
   - Trace a request through the system: entry point → middleware → handler → service → data
   - Note any dependency injection, plugin systems, or dynamic loading

6. **Document conventions**
   - Naming patterns (camelCase, snake_case, kebab-case)
   - Error handling approach (exceptions, result types, error codes)
   - Logging style and levels
   - Test patterns (unit, integration, e2e)
   - Configuration approach (env vars, config files, feature flags)

7. **Analyze dependencies** (if focus area specified)
   - If a focus area was given, deep-dive into those specific files
   - Map imports and function calls to understand coupling
   - Identify shared utilities and how they're used

8. **Write exploration report**
   - Use `file_write` to save to workspace as `codebase_{repo_name}.md`
   - Structure: Tech Stack → Architecture → Key Files → Patterns → Dependencies → Notes
   - Include file paths for every claim

9. **Report findings**
   - Summarize the architecture in the conversation
   - Highlight anything unusual or noteworthy

## Important Notes

- Read actual files — don't guess from directory names alone
- If the repo is large (>100 files), focus on the src/ or lib/ directory first
- Always check for internal documentation (docs/, ARCHITECTURE.md, ADR/)
- Note any code smells or technical debt you spot, but don't judge — just document
