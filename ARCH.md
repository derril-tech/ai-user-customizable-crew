# ARCH.md — User-Customizable AI Crew

## Backend Architecture

### Orchestration (workers)
- crew-builder → generates crew.json, roles.json, workflows.json
- orchestrator → manages agent turn-taking and dependencies
- agent-executor → runs single agent tasks with tools + memory
- safety-enforcer → compliance guardrails, PII scrubbing, redaction
- cost-tracker → logs token usage + alerts
- deliverer → aggregates outputs, uploads artifacts

### Topology
- BFF: Next.js 14
- API: FastAPI 3.11 (/v1/*)
- Workers: Python (CrewAI/LangChain), Node (webhooks)
- Event Bus: NATS + Redis DLQ
- Storage: Postgres (metadata), S3/R2 (artifacts), Redis (cache)
- Observability: OTel, Tempo, Loki, Prometheus, Sentry

### Data Model (Postgres)
- orgs, users, crews, agents, jobs, audit_log tables
- crew.json + roles.json stored as JSONB

### API Surface
- POST /v1/crews — create crew
- GET /v1/crews/:id — fetch crew
- POST /v1/crews/:id/run — execute workflow
- GET /v1/jobs/:id/stream — SSE monitoring

## Frontend Architecture
- Framework: Next.js 14 + Mantine + Tailwind
- State: TanStack Query + Zustand
- SSE client for real-time progress
- Key pages: Dashboard, Crew Builder, Marketplace, Crew Detail, Audit Dashboard

## DevOps
- FE → Vercel
- BE → Render/Fly.io
- DB: Managed Postgres
- CDN/Storage: CloudFront + S3/R2
- IaC: Terraform for DB, Redis, NATS, buckets
- CI/CD: GitHub Actions

## Testing
- Unit: schema validation, compliance enforcement
- Integration: crew.create → run → logs
- E2E: full flow crew run
- Load: 100 concurrent crews
- Chaos: worker crash, API rate-limit
- Security: PII redaction checks
