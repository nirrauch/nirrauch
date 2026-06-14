---
title: "Knowledge Skills (distill / recall / learn)"
created: 2026-06-14
tags: [skills, memory, distill, recall, learn]
summary: "Status and design decisions for the three cross-session knowledge skills: /distill, /recall, /learn."
---

## 2026-06-14 — [KEY] decision: knowledge skills v1 complete and deployed
All three knowledge skills are implemented and live at ~/.claude/skills/. /distill reviews a full session and writes approved entries to nirrauch/.claude/memory/. /recall loads relevant entries silently into context based on query specificity. /learn writes a single high-signal insight immediately without approval. Knowledge files are flat, topic-scoped, project-prefixed (e.g. first-dance-venue.md), append-only, and indexed via MEMORY.md.
