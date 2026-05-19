---
status: accepted
type: adr
date: 2026-05-19
---

# ADR 005: State Management: TanStack Query + Zustand

## Status

Accepted

## Context

The platform has two distinct state categories: server state (weather metrics, location data, chat history fetched from FastAPI) and client state (UI preferences, sidebar toggle, active filters, theme). Mixing these in a single store (e.g., Redux) creates unnecessary complexity, stale-data bugs, and boilerplate. We need a caching strategy for polling weather data every 60 seconds and streaming support for the chatbot.

## Decision

We adopt a dual state management approach:

- **TanStack Query v5** for all server state. It provides automatic caching, background refetching, optimistic updates, and deduplication. Weather metrics use a 60-second `refetchInterval` for near-real-time polling. Query keys are structured as `['weather', locationId]` and `['chat', sessionId]`.
- **Zustand v5** for client-only state. Lightweight (< 1KB), no providers needed, works seamlessly with Server Components since stores are instantiated in Client Components only.
- **SSE (Server-Sent Events)** for Claude chatbot streaming, consumed directly in a Client Component without TanStack Query (streaming is not request/response). Weather metrics use polling rather than WebSockets because the 60-second cadence does not justify persistent connection overhead at pilot scale.

We chose TanStack Query over SWR for its richer devtools, mutation support, and query invalidation patterns. We chose it over Redux Toolkit Query to avoid Redux boilerplate when we have no need for a global reducer tree. Zustand was selected over React Context because Context triggers full subtree re-renders on any state change, while Zustand provides selector-based subscriptions.

## Consequences

- **Positive**: Clear separation of concerns; server state is always fresh via background refetch. Zustand stores are tiny and testable in isolation.
- **Positive**: No context providers needed for Zustand; avoids provider nesting and works cleanly at the Client Component boundary.
- **Negative**: Two libraries to learn, though both have minimal APIs. Developers must correctly choose which tool owns a given piece of state.
- **Mitigation**: Document decision criteria in team standards: "If it comes from the API, use TanStack Query. If it lives only in the browser, use Zustand."
