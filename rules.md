# CI/CD Gatekeeper Coding Rules

These rules are mandatory for all upcoming project implementation work.

## 1) Python Version and Type Hinting
- Python 3.10+ is required.
- All public functions, methods, and module-level variables must include explicit type hints.
- Return types are mandatory.
- Use typed data structures (for example, dataclasses or TypedDict-style contracts) for payloads crossing module boundaries.

## 2) Single Responsibility Principle (Strict)
- Each file must have one clear responsibility.
- No source file may exceed 150 lines.
- If a file approaches 150 lines, split it into focused modules immediately.
- Avoid multi-purpose utility files.

## 3) Modular Architecture
- Keep clear module boundaries:
  - SQL parsing
  - OpenMetadata API wrapper
  - Blast radius assessment
  - Report generation
  - CI entrypoint/orchestration
- Prevent circular imports.
- Keep side effects at boundaries (CLI/workflow entrypoints), not in core logic modules.

## 4) Logging Over Print
- Use the logging library for all runtime output.
- print statements are forbidden in application logic.
- Use log levels consistently: DEBUG, INFO, WARNING, ERROR.
- Never log secrets, tokens, or sensitive identifiers.

## 5) Error Handling and Reliability
- Fail fast on invalid configuration.
- Raise explicit, typed exceptions for recoverable vs non-recoverable failures.
- Add contextual logging on errors without leaking credentials.

## 6) Testability Requirements
- Core logic must be pure and unit-testable.
- External calls (HTTP, GitHub integration) must be isolated behind interfaces/wrappers.
- Add tests for parser edge cases, API error handling, and merge-block decision logic.

## 7) Copilot Operating Protocol (Mandatory)
- Before generating any complex logic, read rules.md and context.md.
- Ground all implementation decisions in the CI_CD Gatekeeper Blueprint.md context.
- When instructed with the phrase "Update the Context Ledger", update context.md sections accurately:
  - Completed Modules
  - Current Focus
  - Known Bugs/Issues
