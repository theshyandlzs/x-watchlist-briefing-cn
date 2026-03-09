---
name: x-watchlist-briefing-cn
description: Generate a Chinese time-window briefing from a fixed watchlist of 129 X accounts across AI, founders, SaaS and apps, go-global, eSIM, indie hacking, OpenClaw, knowledge, and side hustle sectors.

user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - TWITTER_TOKEN
      bins:
        - curl
        - python3
    primaryEnv: TWITTER_TOKEN
    install:
      - id: curl
        kind: brew
        formula: curl
        label: curl (HTTP client)
      - id: python3
        kind: brew
        formula: python
        label: python3
    os:
      - darwin
      - linux
      - win32
  version: 1.0.0
---

# X 129 Watchlist Briefing CN

Generate a Chinese X briefing from the fixed 129-account watchlist.
Output by 9 sectors. Every conclusion must include source tweet links.

This OpenClaw package is parallel to the Codex skill. It does not use `agents/openai.yaml` or Codex MCP wiring.
Instead, it follows the upstream OpenClaw `opentwitter` style and calls the 6551 API directly with `curl` and `$TWITTER_TOKEN`.

## Prerequisites

1. `TWITTER_TOKEN` is present in the environment.
2. `curl` is available.
3. `python3` is available.
4. Resolve the skill root before reading local files or running helper scripts.
   - If `SKILL.md` is not in the current working directory, switch to the installed package root first.
   - Typical roots are `~/.openclaw/skills/x-watchlist-briefing-cn` or your cloned repo root.
   - Do not run `python3 scripts/...` from an unrelated working directory.
5. Read:
   - `references/watchlist.json`
   - `references/opentwitter-openclaw.md`
6. Quick sanity check, from the skill root:
   - `python3 scripts/show_watchlist.py --summary`

## Required Inputs

1. Normalize the user's requested time window.
   - Default end: current Beijing time.
   - Default window: last 48 hours.
2. Normalize output scope.
   - Default: all 9 sectors.
   - If the user asks for specific sectors, filter after loading the watchlist.
3. Write absolute start and end times in the final briefing.

## Workflow

### Step 0: Resolve the package root

1. Before any local file access, confirm the current working directory contains `SKILL.md`.
2. If it does not, switch to the installed skill directory before reading `references/...` or executing `python3 scripts/...`.
3. Use absolute paths if the runtime cannot safely change directories.

### Step 1: Normalize the time window

1. Convert the user's phrasing into absolute Beijing time and UTC.
2. If only an end time is given, default to the previous 48 hours.
3. If only a duration is given, use current Beijing time as the end.
4. Do not write only relative phrases such as `today`, `yesterday`, or `recently`.

### Step 2: Load and deduplicate the watchlist

1. Load all sectors from `references/watchlist.json`.
2. Deduplicate by `handle.lower()` before fetching.
3. Preserve all `sector_tags` for duplicated handles that appear in multiple sectors.
4. Fetch each unique handle only once.

### Step 3: Verify the runtime path

1. Confirm `$TWITTER_TOKEN` is set.
2. Confirm `curl` and `python3` are available.
3. Use the HTTP endpoint notes in `references/opentwitter-openclaw.md`.
4. Do not hardcode a token into this package.

### Step 3.5: Use the stable fetch ladder

For every handle, use this order:

1. Call the account profile endpoint first and capture canonical `screenName`.
2. Use canonical `screenName` for all downstream requests.
3. Try the timeline endpoint first.
4. If timeline returns `400 no tweet`, switch to account-scoped search for the same window.
5. Only mark the handle invalid when profile fails, or both timeline and fallback search fail.

Error handling rules:

- `429`: rate limiting, apply bounded backoff.
- `400 no tweet`: timeline endpoint failure or empty result, not automatic handle invalidation.
- profile success plus timeline failure: continue with search fallback.

### Step 4: Collect candidate posts

Keep only high-signal items inside the target window:

1. original tweets
2. quote tweets with added commentary
3. long posts or threads
4. replies only when they add new information

Ignore:

1. likes
2. empty reposts
3. pure chatter, greetings, giveaways, or no-signal posts

Keep these fields per candidate:

- `handle`
- `canonical_screen_name`
- `display_name`
- `sector_tags`
- `posted_at_utc`
- `posted_at_cn`
- `post_url`
- `post_type`
- `raw_claim`
- `signal_reason`

### Step 5: Rank and separate fact from opinion

1. Cluster by topic first.
2. Merge duplicate discussion threads into one item.
3. For every item, split into:
   - `事实`
   - `观点/判断`
4. Do not write inference as fact.
5. Mark unclear claims as `待证实`.

Priority order:

1. new models, products, launches, or features
2. concrete growth, revenue, SEO, distribution, or monetization numbers
3. actionable AI, Agent, OpenClaw, or indie hacking workflows
4. actionable go-global, eSIM, or overseas phone-number practice
5. frameworks transferable to founders, indie makers, and side hustlers

### Step 6: Write the briefing

You may use these helpers:

- `python3 scripts/render_digest_template.py`
- `python3 scripts/render_digest_template.py --end '2026-03-08T09:00:00+08:00' --hours 168`
- `python3 scripts/render_digest_template.py --start '2026-03-01T09:00:00+08:00' --end '2026-03-08T09:00:00+08:00'`

Default structure:

1. title and absolute window
2. one-paragraph executive summary
3. AI
4. founders
5. SaaS and apps
6. go-global
7. eSIM and overseas phone cards
8. indie developers
9. OpenClaw
10. knowledge sharing
11. side hustle
12. cross-sector signals
13. no-public-update or no-high-signal accounts

Per item format:

- `结论`
- `事实`
- `观点/判断`
- `为什么重要`
- `来源`

Source rules:

1. every item needs at least one original X link
2. no more than 3 links per topic
3. if you must use a second-hand source, label it and lower its weight

### Step 7: Final quality bar

Check every run:

1. absolute start and end are present
2. the full watchlist or an explicitly filtered subset was loaded
3. handles were deduplicated
4. canonical `screenName` was resolved before timeline calls
5. `400 no tweet` used search fallback
6. `429` used bounded backoff
7. all requested sectors still have headings
8. every conclusion has source links
9. facts and opinions are split
10. duplicate cross-sector items are not repeated verbatim
11. empty sectors are stated explicitly instead of hidden

## Failure Patterns To Avoid

1. replacing the fixed watchlist with generic keyword search
2. writing only relative time phrases
3. mixing opinions into facts
4. dropping source links
5. fetching the same handle multiple times because it belongs to multiple sectors
6. treating `400 no tweet` as proof the account is dead
7. treating `429` as a content failure instead of backoff
8. dumping low-signal posts into the briefing
9. running `python3 scripts/...` from a working directory that is not the skill root

## Quick Commands

Run these from the skill root:

1. `python3 scripts/show_watchlist.py --summary`
2. `python3 scripts/show_watchlist.py --duplicates`
3. `python3 scripts/show_watchlist.py --sector ai`
4. `python3 scripts/render_digest_template.py`
5. `python3 scripts/render_digest_template.py --end '2026-03-08T09:00:00+08:00' --hours 168`
