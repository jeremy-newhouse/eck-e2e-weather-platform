---
status: accepted
type: adr
date: 2026-05-19
---

# ADR 003: Authentication — JWT

## Status

Accepted

## Context

The platform needs authentication for user accounts, chatbot session continuity, and API access control. Options considered: server-side sessions (stored in Redis/DB) versus stateless JWT tokens.

Deployment on ECS Fargate means multiple task instances behind an ALB, making sticky sessions undesirable. The frontend is a Next.js SPA that communicates via REST API.

## Decision

Use JWT-based authentication with the following design:

**Token strategy:**

- Access token: short-lived (15 minutes), signed with HS256 using a secret from AWS Secrets Manager.
- Refresh token: longer-lived (7 days), stored in the database with rotation on use (one-time use, issues new refresh token on each refresh).
- Tokens issued as HTTP-only, Secure, SameSite=Strict cookies for the web client. API clients receive tokens in response body.

**Why JWT over sessions:**

- Stateless verification eliminates per-request database lookups for auth, supporting the p50 < 100ms target.
- Horizontally scalable without shared session store -- any Fargate task can validate tokens independently.
- Simpler infrastructure (no Redis dependency solely for sessions).

**Security considerations:**

- Short access token TTL limits exposure window from token theft.
- Refresh token rotation detects reuse (if a rotated token is presented, invalidate the entire family).
- Token revocation for logout/password-change handled via a lightweight database blocklist checked only when refresh tokens are presented.
- Secrets rotated via AWS Secrets Manager with graceful dual-key validation during rotation windows.

## Consequences

- No per-request session lookup improves latency and reduces database queries per request (supports < 5 query budget).
- Token revocation is eventually consistent (up to 15 minutes for access token expiry); acceptable for pilot scale.
- Refresh token rotation adds implementation complexity but prevents long-lived token theft.
- If immediate revocation becomes required, a Redis-based token blocklist can be added without architectural change.
