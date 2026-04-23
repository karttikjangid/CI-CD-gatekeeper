# CI/CD Gatekeeper Project Plan

## Mission
Build a Python-based GitHub Action that detects SQL-driven blast radius risk in Pull Requests by combining static SQL parsing with OpenMetadata lineage checks, then blocks merges when critical downstream assets are impacted.

## 3-Day Development Phases

### Day 1: API Wrapper (OpenMetadata REST Integration)

**Primary Goal**
Create a reliable, testable wrapper for OpenMetadata REST API interactions.

**Scope**
- Define API client boundaries for auth, requests, retries, and response validation.
- Support downstream lineage retrieval for a given table entity.
- Standardize error handling for auth failures, not-found entities, and transient server errors.

**Deliverables**
- API contract documentation for lineage lookup inputs and outputs.
- Planned module boundaries for auth, transport, and lineage retrieval.
- Test scenarios for success, timeout, 401/403, 404, and 5xx failures.

**Exit Criteria**
- The wrapper design can deterministically fetch downstream lineage for a table.
- Error behavior is documented and ready for implementation.

### Day 2: Parsing Logic (SQL Change Detection)

**Primary Goal**
Define parsing logic that extracts only mutated target tables from SQL changes in PR files.

**Scope**
- Parse SQL using SQLGlot AST traversal.
- Identify target tables for DDL/DML mutations (for example: CREATE, ALTER, DROP, UPDATE, INSERT, DELETE).
- Ignore read-only references from SELECT/JOIN unless part of a mutation statement.
- Include handling approach for dbt workflows (compiled SQL or manifest-based path).

**Deliverables**
- Parser behavior specification with accepted statement classes.
- Table name normalization strategy aligned to OpenMetadata FQN matching.
- Test matrix covering multi-statement files, dialect variance, and parse failures.

**Exit Criteria**
- Parsing design clearly separates mutation targets from source references.
- Output contract is defined for downstream impact assessment.

### Day 3: GitHub Action Deployment (Merge Governance)

**Primary Goal**
Operationalize the gatekeeper in PR CI so critical blast radius blocks merges with clear feedback.

**Scope**
- Configure workflow trigger on PR events with SQL path filtering.
- Define secure secret usage for OpenMetadata host/token.
- Design reporting flow that posts Markdown impact summaries to the PR.
- Enforce merge blocking via non-zero exit code when critical assets are detected.

**Deliverables**
- GitHub Actions workflow blueprint.
- PR comment/report template for pass/fail outcomes.
- Governance rules for failure criteria and bypass process.

**Exit Criteria**
- CI flow is fully specified from changed-file detection to merge block decision.
- Developer feedback loop is clearly documented.

## Definition of Completion
- Day 1 through Day 3 artifacts are documented and implementation-ready.
- Standards in rules.md and state tracking in context.md are integrated into the development workflow.
