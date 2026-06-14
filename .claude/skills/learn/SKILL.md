---
name: learn
description: Use when the user invokes /learn [insight]. Immediately writes a single key insight, decision, or constraint to the persistent knowledge base without requiring approval. Use for capturing a specific realization mid-session — not a full session review (that's /distill). Examples: /learn first-dance: venue confirmed as outdoor, /learn we decided to drop Supabase for Postgres directly.
---

# /learn — Single Insight Capture

Write one key insight to the knowledge base immediately. No approval step — execute and confirm.

## Step 1: Parse the Insight

Extract from the user's message:

- **Topic / project** — what this knowledge belongs to (infer from the query or current working directory if not explicit)
- **Insight** — the core fact, decision, or constraint to preserve
- **Contradicts** — does this directly contradict something that likely exists in the knowledge base? Use judgment; don't read every file to check, but if the topic is one you've already recalled or distilled this session, check for conflicts.

## Step 2: Route to the Right File

Read `MEMORY.md`:
```
/Users/nirrauch/repos/nirrauch/.claude/memory/MEMORY.md
```

Find the best matching spoke file using the same rules as `/distill`:
- Project-specific file if one exists (e.g., `first-dance-venue.md`, `nirrauch-travel-planner.md`)
- Generic topic file if the knowledge is explicitly cross-project
- Create a new file if no match exists (use `[project]-[topic].md` naming)

If creating a new file, use this frontmatter:
```yaml
---
title: "[Topic Name]"
created: YYYY-MM-DD
tags: [tag1, tag2]
summary: "One sentence describing what this file covers."
---
```

## Step 3: Write the Entry

Append to the bottom of the spoke file:

```markdown
## YYYY-MM-DD — [KEY] [type]: [short title]
[The insight in 1–3 dense sentences, written for a future agent.]
[If contradiction: SUPERSEDES filename.md:LINE — "[prior entry title]"]
```

The `[KEY]` marker distinguishes `/learn` entries from `/distill` entries — these are single high-signal insights that should be weighted heavily when a future agent scans the file.

If this contradicts a prior entry:
1. Keep the old entry as-is
2. Add `SUPERSEDES filename.md:LINE — "[prior entry title]"` on the line after the insight
3. Annotate the old entry's line in `MEMORY.md` with `[SUPERSEDED → filename.md:line]`

## Step 4: Update MEMORY.md

- If a new spoke file was created, add it to the index: `- [Title](filename.md) — [summary]`
- If an existing file was updated with a superseding entry, annotate the index line

## Step 5: Commit and Push

```bash
cd /Users/nirrauch/repos/nirrauch
git add .claude/memory/
git commit -m "knowledge: [brief one-line description of the insight]"
git push origin main
```

## Step 6: Confirm to the User

After pushing, confirm in one line:
> Learned: [title] → [filename.md]

If a contradiction was detected and resolved, add:
> Superseded: [prior entry title] at [filename.md:line]
