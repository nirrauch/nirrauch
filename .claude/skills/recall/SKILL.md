---
name: recall
description: Use when the user invokes /recall [query]. Retrieves relevant knowledge from the persistent knowledge base at nirrauch/.claude/memory/ and loads it silently into context. Always requires a topic or question argument — e.g. /recall first-dance song selection, /recall auth decisions, /recall travel planner broadly.
---

# /recall — Knowledge Retrieval

Retrieve knowledge from the persistent knowledge base and load it silently into your context. Do not surface the raw knowledge file contents to the user — use them to inform your responses.

## Step 1: Parse the Query

Extract two signals from the user's query:

- **Topic** — what subject area or project they're asking about
- **Specificity** — how broad or narrow the request is

Specificity guides how much you load:

| Query form | Specificity | Load strategy |
|---|---|---|
| `/recall first-dance song selection` | Narrow | Relevant entries only from the matching file |
| `/recall first-dance auth` | Moderate | All entries in the matching section or file |
| `/recall first-dance broadly` / `/recall first-dance project` | Broad | Full file(s) for that project |
| `/recall all decisions` | Cross-cutting | Scan MEMORY.md for all matching entries across files |

## Step 2: Read MEMORY.md

Read the index:
```
/Users/nirrauch/repos/nirrauch/.claude/memory/MEMORY.md
```

Scan for files whose title or summary matches the query topic. This is your routing step — identify candidate files before loading anything else.

If no files in the index look relevant to the query, stop here and tell the user explicitly:
> "No knowledge found for '[query]'. Nothing has been distilled on this topic yet."

## Step 3: Load Relevant Content

Based on the candidate files identified and the query specificity:

**Narrow query** — read the candidate file(s), then extract only the dated entries whose titles or content directly match the query. Load those entries into context. Skip the rest of the file.

**Moderate query** — read and load the full candidate file.

**Broad / project-wide query** — read and load all files whose title starts with the project name or whose summary mentions the project.

**Cross-cutting query** — read MEMORY.md summaries and load the specific sections or files that match, potentially across multiple topic files.

When loading partial entries from a file, preserve the entry's full text (including its `SUPERSEDES` line if present) — never truncate a single entry.

## Step 4: Handle Superseded Entries

If a loaded entry contains a `SUPERSEDES filename.md:LINE` reference:

- That prior entry is historical context only — do not act on it
- The current (newer) entry is the authoritative knowledge
- You may silently note the evolution in your understanding without surfacing the full chain to the user

## Step 5: Proceed Silently

Do not summarize, quote, or acknowledge the recalled content to the user. Use it as background context to inform your next response. The user invoked `/recall` so they already know you have the context — they don't need to see it repeated back.

The one exception: if the recalled knowledge directly contradicts something the user just said or assumed, surface that contradiction explicitly rather than silently ignoring it.
