# ADR 0001: RPC-first CLI

## Status

Accepted

## Context

`indoo` is a CLI for working with Odoo data. There are many possible access
paths around Odoo itself, including direct SQL, local scripts, and container-
specific workflows.

Those alternatives create product drift. They also pull in environment details
that are outside the Odoo CLI contract, such as PostgreSQL access, Docker
container layout, and database credentials.

## Decision

`indoo` works through Odoo RPC.

Direct database access is out of scope for the normal `indoo` workflow.
Docker-specific access paths are also out of scope.

If work on `indoo` repeatedly reaches for another tool to inspect or mutate
Odoo data, treat that as a missing CLI feature first.

## Consequences

Positive:
- one technical access model
- no Docker dependency in the normal workflow
- behavior stays aligned with Odoo permissions and ORM behavior
- simpler mental model for users and agents

Negative:
- some debugging tasks may feel slower than direct SQL
- discovery gaps must be solved in the CLI instead of bypassed externally
