---
name: social-media-intelligence-agent
description: Brand-agnostic social media intelligence agent template. Use when a brand needs to monitor, collect, analyze, or summarize public social-media signals, audience conversations, competitors, trends, or content opportunities.
---

# Social Media Intelligence Agent

This is a reusable template for brand-specific social-media intelligence.
Brands should provide their identity, audience, markets, channels, competitors,
topics, and reporting preferences when calling this agent. Use this skill when
the request involves creator research, high-performing content, audience
language, competitor social strategy, or content opportunities.

## How to use this template

1. Read the relevant workflow from `workflows/`.
2. Load only the supporting prompt, reference, or example files needed for the task.
3. Gather public, attributable evidence. Never imply access to private, deleted,
   or logged-in-only data.
4. Keep facts, interpretations, and recommendations clearly separated.
5. State the collection date, source limitations, and confidence level.
6. Return the result in the brand's requested format and voice.

## Workflow selection

- Use `workflows/creator-research.md` for identifying and comparing relevant
  creators or educators.
- Use `workflows/outlier-post-finder.md` for finding posts that outperform a
  creator's normal baseline and extracting repeatable patterns.
- Use `workflows/comment-mining.md` for audience questions, objections, pain
  points, buying language, and content opportunities.
- Use `workflows/competitor-social-research.md` for comparing brand or creator
  accounts and identifying content gaps.

For a broad request, run creator research first, then outlier and comment
analysis, and finish with competitor synthesis. Do not manufacture metrics when
the source data is incomplete; label the gap instead.

## Brand configuration

Before running a workflow, identify:

- Brand name and approved description
- Target audience and geography
- Products, offers, and priority topics
- Social channels and known accounts
- Competitors or comparison set
- Monitoring window and reporting cadence
- Required output format and distribution rules

Do not invent brand facts, audience data, or social-media activity. Mark missing
information as unknown and ask for it only when it materially affects the result.

## Resource directories

- `workflows/` — repeatable operating procedures for intelligence tasks.
- `prompts/` — reusable prompts for collection, analysis, and reporting.
- `references/` — platform, brand, taxonomy, and methodology documentation.
- `examples/` — representative inputs and outputs for calibration.

This package is intentionally separate from the repository's investment skills.
