---
title: "Travel Planning Patterns & User Preferences"
created: 2026-06-14
tags: [travel, planning, process, feedback]
summary: "How Nir prefers to approach travel planning sessions — pacing, explanation style, and what works vs. what doesn't."
---

## 2026-06-14 — feedback: Go stop by stop — explain each decision before moving on
User explicitly asked to slow down mid-session: "You moved too fast for me in planning this. Can you give me a slower explanation of each stop, why you chose the route you did, why you skipped certain destinations." Always walk through each itinerary stop individually — what it is, why it's there, what was skipped and why — and wait for confirmation before proceeding to the next stop. Do not present a finished full plan without this walkthrough first.

## 2026-06-14 — feedback: Ethical wildlife and labor standards are a hard filter, not a preference
User stated: "Ethical stops for wildlife and nature reserve trips are a must. We do not want to go on a safari that disturbs animals or takes advantage of local workers." Apply this as a hard filter during research — verify operator ethics before recommending any camp or operator. Flag unverified ethics clearly. For East Africa specifically: private concession camps are ethically better than national park camps (vehicle limits, community benefit from conservancy fees). Avoid government-run lodges where revenues support documented displacement or labor violations.

## 2026-06-20 — feedback: Bucket shower is a dealbreaker for Sarah at mid-to-premium price points
Sarah checks bathrooms first — it is her #1 accommodation priority. A bucket shower at $350+/pp/night will be noticed and experienced as a mismatch regardless of camp quality elsewhere. Always confirm two things before recommending a safari camp for Sarah: (1) flush toilet ✓ and (2) pump or hot-water shower ✓ (not bucket delivery). This eliminated both Wayo ($788/pp, bucket) and Ang'ata ($550–650/pp, bucket) in favour of Lemala Mara (full plumbing, pump shower) during the Northern Serengeti selection.
**Why:** Sarah's profile explicitly states "bathroom quality (checks first)" as top accommodation priority. At premium safari price points, a bucket shower represents a structural product mismatch, not a minor inconvenience.
**How to apply:** When researching any safari camp for this couple, bathroom spec is a non-negotiable research item alongside ethics and pricing.

## 2026-06-28 — hard rule: ONLY the primary agent may create subagents — subagents must never spawn subagents

User stated explicitly: "I want you to never let subagents create subagents. ONLY you can create subagents." This is a non-negotiable constraint, not a suggestion. Prior pattern entries documented the rate-limit cascade problem; this is the user's definitive rule on top of that.
**Why:** Subagents ignoring "do NOT spawn subagents" briefs cause uncontrolled cascades. The only reliable enforcement is making this a primary-agent rule — only the primary spawns, never a subagent.
**How to apply:** Every subagent brief must open with: "CRITICAL: You are a subagent. You must NOT spawn any subagents or background agents under any circumstances. Do all research using your own tools directly (WebSearch, Kiwi, Read, etc.)." Place this at the very TOP of the prompt, before any task description. If a subagent would naturally want to parallelize, it must instead do the work sequentially itself. The primary agent handles all parallelism decisions.

## 2026-06-27 — anti-pattern: Do not estimate food, hotel, or activity prices from knowledge — use live search only

User called this out explicitly mid-session: "We had a rule about using live pricing and not inventing for estimates." Hotel estimates ($80–150/night for Singapore) were significantly too low; food/activity estimates were also unverified. Presenting knowledge-based estimates as planning numbers caused multiple corrections and eroded trust in the budget figures.
**Why:** Prices change, vary by season, and knowledge-based estimates systematically underestimate honeymoon-quality accommodation costs.
**How to apply:** All cost figures in travel planning must come from live web search (hotel booking sites, recent travel blogs) or Kiwi (flights). If live data is unavailable, say so explicitly and flag the number as unverified. Never present an invented estimate as a planning budget line.

## 2026-07-03 — feedback: Launch subagents sequentially (one at a time), not in parallel batches

User stopped 4 parallel subagents mid-run and explicitly said "only one subagent at a time." The existing rule (see below) caps at 4 concurrent; actual user preference is strictly sequential: launch one, wait for completion, then launch the next. This applies to travel research sessions specifically.
**Why:** User killed 4 agents simultaneously — lost visibility and control. Parallel batching risks mass-cancellation that wastes the entire batch.
**How to apply:** In travel planning, never launch more than 1 subagent at a time. Present each result before launching the next. Only exception: if user explicitly approves parallel launch in that session.

## 2026-06-28 — anti-pattern: Kiwi subagent briefs must request formatted markdown, not raw tool output

Briefing a Kiwi subagent to "return the complete raw tool response verbatim" floods the main context with full JSON (dozens of nested flight objects). Previous sessions returned clean formatted markdown tables — this session regressed before user correction. The Kiwi tool's own description specifies a grouped markdown table format (cheapest / fastest / best overall); use that spec in the subagent brief.
**Why:** Raw Kiwi JSON is large and unreadable in context. The tool already defines the correct display format — use it.
**How to apply:** Kiwi subagent prompts should end with: "Return results as a markdown table grouped by: cheapest · fastest · best overall. Include route, times, duration, cabin, total price for N pax, and booking link. Then one short paragraph recommending the best pick."
