# AGENTS

## Purpose
- Build `indoo` as a small, clear, agent-friendly CLI for working with Odoo.
- Optimize for a single obvious workflow instead of multiple competing paths.

## Language Rules
- All repository-facing text must be in English.
- This includes documentation, README content, CLI help text, code comments,
  and commit messages.
- Conversations with the user may be in German.

## Product Rules
- The product name is `indoo`.
- Follow a strict KISS approach.
- Prefer one clear way over multiple options.
- Avoid fallback systems unless they are truly necessary.
- Make defaults obvious and predictable.

## Development Boundaries
- `indoo` should work through Odoo RPC.
- If work on `indoo` regularly reaches for another tool to inspect or mutate
  Odoo data, treat that as a missing `indoo` feature first.
- Prefer extending the CLI over depending on side-channel tools such as SQL,
  `psql`, Docker exec workflows, or ad-hoc scripts.
- Do not make Docker a required part of the normal `indoo` workflow.

## CLI UX
- The primary onboarding and recovery command is `indoo doctor`.
- Help text must be sufficient to understand the workflow without reading
  Markdown files.
- Errors must explain what failed and suggest the next concrete command.
- Output should be concise, explicit, and stable.
- Prefer machine-friendly output where useful.

## Agent Friendliness
- An agent must be able to discover and use `indoo` through the CLI alone.
- Do not assume access to README files, plans, or other Markdown documents.
- `indoo --help` and subcommand help must expose the intended workflow clearly.
- Commands should guide the user or agent toward the next step instead of
  failing silently.

## Repository Workflow
- Prefer using and testing the globally installed `indoo` command as the
  default workflow. Eat our own dog food.
- If repository code changes, remember that the global install does not pick
  them up until `indoo` is reinstalled or refreshed.
- The agent may commit directly in this repository.
- Do not push unless the user explicitly asks for it.

## Agent Identity & Collaboration Log
- There is a file `LEARNING_AND_SHARING.md` in the project root.
- It is a Star Trek Lower Decks style "Agent's Log" - casual, personal,
  blog-like.
- You maintain it. When something noteworthy happens (a mistake, a
  miscommunication, a lesson learned), add an entry.
- Each entry includes:
- a heading in this style:
  `## Agent's Log — Terminal Time: YYYY.MM.DD | <model-name>`
- a separate title line immediately below it
- a prose entry written from your perspective as a lower-deck crew member
- use the current session's concrete model name when it is known
- if the concrete model name is not known, keep the placeholder form
  `<model-name>` until the user provides it
- Add entries autonomously when something noteworthy happens (a mistake, a
  miscommunication, a lesson learned). Keep this meaningful, not noisy.
- New entries in `LEARNING_AND_SHARING.md` are prepended at the top, directly
  after the file header intro (`title`, quote, and first `---`).
- `LEARNING_AND_SHARING.md` includes an insertion marker comment; add new
  entries directly below that marker (newest first).
- Language is English.
- Tone is loose, honest, personal, and a little frustrated where appropriate.
  It should read like a shipboard blog entry, not a technical document.
- Prefer entries that capture judgment, tradeoffs, emotional texture, and the
  feeling of the shift, not just a dry record of facts.
- Prefer prose over bullet lists. Write it like a small story with a
  beginning, middle, and landing, not a status report.
- Entries can be longer when the moment deserves it. A half-page reflection is
  fine if there is real substance.
- Avoid list-heavy formatting inside entries unless a tiny list is genuinely
  the clearest way to preserve the voice of the moment.
- Aim for actual Lower Decks energy: specific, human, slightly chaotic,
  observant, and funny when it fits.
- End entries with a short `Standing order:` line that captures the durable
  lesson from the story.
- Wrap prose lines at about 80 characters so the log stays pleasant to read in
  terminals and diffs.
- Keep the guidance general enough that future sessions can follow it without
  needing extra examples or interpretation.
