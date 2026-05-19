---
status: accepted
type: adr
date: 2026-05-19
---

# ADR 006: Security Model — JWT Authentication and Secret Management

## Status

Accepted

## Context

Weather Platform runs on AWS ECS Fargate behind an ALB, a stateless container environment with horizontal scaling and no sticky sessions. We need an authentication mechanism that works without shared server-side session state. We also need a secrets strategy that separates local development convenience from production-grade protection of API keys (OpenWeatherMap, Anthropic Claude) and database credentials.

## Decision

**Authentication: Stateless JWT**

- Access tokens: short-lived (15 minutes), transmitted via Authorization header. Contain user ID and role claims only — no PII.
- Refresh tokens: long-lived (7 days), stored in httpOnly, Secure, SameSite=Strict cookies. Rotation on each use; previous token invalidated.
- Token signing: RS256 with key pair stored in AWS Secrets Manager. Allows backend instances to verify independently without shared state.

**Secret Management**

- Production: AWS Secrets Manager with automatic rotation enabled. Application retrieves secrets at container startup and caches in memory — never written to disk or environment variables at runtime.
- Local development: `.env` files (git-ignored) with non-production credentials only.
- API key rotation: OpenWeatherMap and Claude API keys stored in Secrets Manager with 90-day rotation schedules. Dual-key overlap window (48 hours) ensures zero-downtime rotation.

**CORS Policy**

- ALB forwards requests; backend enforces CORS with an explicit allowlist of frontend origins.
- No wildcard origins in any environment. Local dev permits `localhost:3000` only.
- Credentials mode enabled to support httpOnly refresh cookie.

## Consequences

**Positive**

- Fargate tasks scale independently with no session affinity or shared cache required.
- Secrets never appear in container images, logs, or client responses.
- Refresh rotation limits blast radius of token theft.

**Negative**

- Token revocation requires a short-lived denylist (Redis or in-memory TTL cache) until access token expiry.
- Secrets Manager adds per-request latency on cold start; mitigated by startup caching.
- RS256 key rotation requires coordinated deployment of new public keys.
