# OpenTwitter For OpenClaw

This OpenClaw package follows the same authentication model as the upstream `opentwitter` OpenClaw skill from `6551Team/opentwitter-mcp`.

## Required Environment

- `TWITTER_TOKEN`
- `curl`
- `python3`

Default API base:

- `https://ai.6551.io`

Authorization header:

```bash
-H "Authorization: Bearer $TWITTER_TOKEN"
```

## Core Endpoints

### 1. Account profile lookup

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_user_info" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"elonmusk"}'
```

Use this first to get canonical `screenName`.

### 2. Timeline fetch

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_user_tweets" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"elonmusk","maxResults":20,"product":"Latest","includeReplies":false,"includeRetweets":false}'
```

### 3. Account-scoped search fallback

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_search" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fromUser":"elonmusk","sinceDate":"2026-03-01","untilDate":"2026-03-08","excludeReplies":false,"excludeRetweets":false,"product":"Latest","maxResults":20}'
```

## Stable Fetch Ladder

For every handle, use this order:

1. `twitter_user_info` to verify the account and capture canonical `screenName`
2. `twitter_user_tweets` with canonical `screenName`
3. `twitter_search` with `fromUser=canonical_screen_name` when timeline returns `400 no tweet`

Interpretation rules:

- `400 no tweet` does not prove the handle is invalid
- `429` is rate limiting, not a content verdict
- profile success plus search success means keep the account
- only mark an account as invalid when profile fails, or both timeline and fallback search fail

## Backoff Strategy

For `429` responses:

1. retry after 2 seconds
2. retry after 5 seconds
3. retry after 15 seconds
4. insert a short pause after every 10-15 handles

## Absolute Time Discipline

Always convert the requested window to absolute Beijing time and UTC before fetching.
Do not summarize using only relative phrases such as "today" or "recently".
