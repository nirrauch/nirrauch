---
name: distill
description: Use when the user invokes /distill, or at the end of any session where meaningful decisions were made, new technical approaches were established, or prior decisions were revisited. Distills the current conversation into the persistent knowledge base at nirrauch/.claude/memory/. Use this to preserve learnings, decisions, and contradictions across sessions.
---

# /distill — Session Knowledge Distillation

Distill the current conversation into the persistent knowledge base. Knowledge is append-only — never overwrite or delete historical entries.

## What to Distill

Distill anything that would change how a future agent approaches work:

- **Decisions** — architectural, tooling, or product choices and their rationale
- **Contradictions or evolutions** — when this session changes or supersedes a prior decision
- **New learnings** — non-obvious insights, debugging findings, discovered constraints
- **Established patterns** — approaches that worked and should be repeated
- **Anti-patterns** — approaches that failed and should be avoided

Skip: implementation details already in code, transient debugging steps with no lasting insight, conversation pleasantries.

## Step 1: Read the Knowledge Index

Read `MEMORY.md` from the nirrauch repo:
```
/Users/nirrauch/repos/nirrauch/.claude/memory/MEMORY.md
```

If it doesn't exist yet, treat the knowledge base as empty — you'll create it in Step 5.

Also read the frontmatter (first 20 lines) of any spoke file whose summary looks relevant to today's session topics. This tells you which files to append to vs. create new.

## Step 2: Identify Distillation Candidates

Scan the full conversation and extract candidates. For each, note:

- **Topic** — what area of knowledge this belongs to (e.g., `auth`, `api-conventions`, `travel`)
- **Type** — decision / learning / pattern / anti-pattern / contradiction
- **Content** — the insight in 1–3 sentences, written for machine reading (dense, no filler)
- **Contradicts** — if this changes a prior entry, identify the exact file and line number: `filename.md:42`

## Step 3: Draft Proposed Entries

For each candidate, draft the entry it would add. Format:

```markdown
## YYYY-MM-DD — [type]: [short title]
[Dense 1–3 sentence description. Written for a future agent, not a human.]
[If contradiction: SUPERSEDES filename.md:LINE — "[prior entry title]"]
```

Group candidates by target file.

## Step 4: Present Summary for Approval

Show the user a bulleted list before writing anything:

```
Proposed additions:

• [topic.md] decision: [title]
  → [one-line preview of the entry]

• [topic.md] learning: [title]
  → SUPERSEDES topic.md:23 — "[prior entry title]"
  → [one-line preview]

• NEW FILE: [topic.md]
  → [one-line preview]
```

Wait for explicit approval before proceeding. If the user edits or rejects items, update accordingly.

## File Scope: New File vs. Append to Existing

**Append to an existing file when:**
- The knowledge belongs to the same topic and project as an existing file
- The existing file has room (<150 lines of body content)
- The new entry is a follow-on, contradiction, or evolution of entries already in that file

**Create a new file when:**
- No existing file covers this topic
- An existing file is getting long (>150 lines body) and the new entry starts a clearly separable sub-topic
- The knowledge is specific to a different project than the closest matching file

**File naming conventions:**
- Default to project-specific names: `[project]-[topic].md` (e.g., `nirrauch-travel-planner.md`, `nirrauch-memory-skills.md`)
- Use a generic topic name only when the knowledge explicitly applies across all projects (e.g., `git-conventions.md`, `api-design.md`)
- When in doubt, prefer project-specific — it is better to have two files that could have been merged than one file that mixes unrelated project contexts
- Use lowercase kebab-case, no spaces

## Step 5: Write to Knowledge Files

For each approved entry:

1. **Append** the dated entry to the correct spoke file under `/Users/nirrauch/repos/nirrauch/.claude/memory/`
2. Files are organized by topic only — flat directory, no type-based subdirectories (e.g., `nirrauch-auth.md`, `api-conventions.md`)
3. Never modify existing entries — only append below them
4. If a new spoke file is needed, create it with this frontmatter:

```yaml
---
title: "[Topic Name]"
created: YYYY-MM-DD
tags: [tag1, tag2]
summary: "One sentence describing what this file covers — used by agents to decide relevance without reading the body."
---
```

5. Update `MEMORY.md` index:
   - Add new spoke files as: `- [Title](filename.md) — [summary]`
   - If an entry is superseded, append `[SUPERSEDED → filename.md:line]` to that index line
   - Never remove old index entries — only annotate them

## Step 6: Commit and Push

```bash
cd /Users/nirrauch/repos/nirrauch
git add .claude/memory/
git commit -m "memory: distill session — [brief topic summary]"
git push origin main
```

Use a typed commit prefix so git log is queryable: `memory:` for general knowledge, `decision:` for architectural choices.

## Knowledge File Conventions (for future agents)

- **`MEMORY.md`** — the index. Always loaded. <200 lines. Each entry: `- [Title](file.md) — one-line hook`. This is how an agent routes to the right spoke file without reading everything.
- **Spoke files** — topic-specific, flat in the memory directory, loaded on demand. Always start with YAML frontmatter including a `summary` field.
- **Dated entries** — always `## YYYY-MM-DD — [type]: [title]`, appended at bottom of the relevant spoke file
- **Line references** — when superseding, always include `SUPERSEDES filename.md:LINE` so a future agent can follow the decision chain without re-reading history

## Contradiction Handling

When this session's knowledge contradicts or evolves a prior entry:

1. Keep the old entry exactly as-is
2. Append the new entry below it with `SUPERSEDES filename.md:LINE — "[prior entry title]"`
3. In `MEMORY.md`, append `[SUPERSEDED → filename.md:line]` to the old entry's index line

A future agent reading the index will see the superseded flag immediately and navigate directly to the current entry.
