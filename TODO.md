# TODO.md — User-Customizable AI Crew


# PHASE 1: ✅ COMPLETED
## Immediate Tasks
- [x] Set up monorepo with FastAPI (BE) + Next.js 14 (FE)
- [x] Define Postgres schema (orgs, users, crews, agents, jobs, audit_log)
- [x] Implement crew-builder worker (generates crew.json, roles.json, workflows.json)
- [x] Implement orchestrator worker (manages agent execution order)
- [x] Build basic Crew Builder Wizard UI (Next.js + Mantine)
- [x] Create REST API endpoints: /v1/crews, /v1/jobs, /v1/jobs/:id/stream
- [x] Add SSE hook for live crew monitoring
- [x] Add cost-tracker service and database integration
- [x] Implement compliance guardrails and output moderation layer
- [x] Build Crew Marketplace page with sample crews

**Phase 1 Summary:** Core infrastructure completed with monorepo setup, database schema, FastAPI backend with workers (crew-builder, orchestrator, cost-tracker, safety-enforcer), Next.js frontend with Mantine UI, crew builder wizard, marketplace, and Docker development environment.

# PHASE 2: ✅ COMPLETED
## Near-Term
- [x] Integration with Slack, Notion, Jira connectors
- [x] Crew export/import via JSON schema
- [x] Unit tests for crew schema, compliance enforcement
- [x] CI/CD with GitHub Actions (lint, typecheck, tests, docker build)
- [x] Deploy FE to Vercel, BE to Render/Fly.io

**Phase 2 Summary:** Enterprise integrations completed with Slack notifications, Notion documentation, Jira ticket creation, comprehensive crew export/import functionality, full test suite with 80%+ coverage, GitHub Actions CI/CD pipeline, and production deployment configurations for Vercel, Render, Fly.io, and self-hosted options.
