# Architectural Decision Records (ADRs)

This section documents the key architectural decisions made during the development of the China Economic Data Analysis package.

## What are ADRs?

Architectural Decision Records (ADRs) are documents that capture important architectural decisions made along
with their context and consequences. They help maintain institutional knowledge and provide context for future
development decisions.

## ADR Index

| ADR                                       | Title                   | Status   | Date       |
| ----------------------------------------- | ----------------------- | -------- | ---------- |
| [ADR-001](001-python-version-strategy.md) | Python Version Strategy | Accepted | 2025-01-01 |
| [ADR-002](002-type-checking-strategy.md)  | Type Checking Strategy  | Accepted | 2025-01-01 |
| [ADR-003](003-documentation-strategy.md)  | Documentation Strategy  | Accepted | 2025-01-01 |

## ADR Template

When creating new ADRs, use this template:

```markdown
# ADR-XXX: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded]

## Context

[Describe the context and problem statement]

## Decision

[Describe the decision made]

## Consequences

[Describe the consequences of the decision]

## Alternatives Considered

[List alternatives that were considered]

## References

[Any relevant references]
```

## Contributing ADRs

When making significant architectural decisions:

1. Create a new ADR using the template
2. Number it sequentially (ADR-004, ADR-005, etc.)
3. Discuss with the team
4. Update this index
5. Commit the ADR with your changes
