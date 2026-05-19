---
status: accepted
type: adr
date: 2026-05-19
---

# ADR 004: Frontend Architecture: Next.js App Router

## Status

Accepted

## Context

The Weather Platform needs a frontend framework that supports server-side rendering for fast initial loads of weather dashboards, client-side interactivity for charts and chat, and a clear component model for a small team to maintain. We evaluated Next.js 16 (App Router), Remix, and SvelteKit.

Key requirements: SEO-friendly weather pages, sub-2.5s LCP, streaming support for the Claude chatbot, and TypeScript-first development. The team has existing React expertise, and the backend is a separate FastAPI service requiring clean API integration.

## Decision

We adopt Next.js 16 with the App Router and the following SSR/CSR strategy:

- **Server Components by default** for all data-fetching pages (dashboard, location lists, settings). These fetch weather data via server actions calling the FastAPI backend, eliminating client-side waterfalls.
- **Client Components only at interaction boundaries**: Recharts visualizations (lazy-loaded via `next/dynamic`), the Claude chatbot panel (SSE streaming), and form-heavy UI (react-hook-form).
- **Route groups** organize features: `(dashboard)`, `(chat)`, `(settings)`.

We chose Next.js over Remix because of superior static/dynamic rendering granularity, mature ecosystem (Vercel/AWS adapters), and the team's React familiarity. SvelteKit was ruled out due to smaller ecosystem and team ramp-up cost for a pilot-phase project.

## Consequences

- **Positive**: Server Components reduce client bundle size (target < 200KB initial JS). Streaming SSR enables progressive rendering. Strong TypeScript integration with App Router conventions.
- **Positive**: Colocation of data fetching with route segments simplifies reasoning about loading states.
- **Negative**: App Router's evolving APIs require tracking upstream changes. Client/Server boundary mistakes cause runtime errors that are only caught at build time.
- **Mitigation**: Enforce `"use client"` directive via ESLint rule; document boundary patterns in team standards.
