# PLAN.md — User-Customizable AI Crew

## Milestones

### Milestone 1: Core Infrastructure
- Monorepo setup (FE + BE + Workers)
- Postgres schema migration applied
- NATS + Redis event bus configuration
- Basic FastAPI endpoints running

### Milestone 2: Crew Creation & Management
- Crew Builder Wizard (multi-step UI)
- Backend crew-builder worker
- Persist crew.json, roles.json, workflows.json
- Marketplace page with starter templates

### Milestone 3: Crew Execution & Monitoring
- Orchestrator worker implemented
- Agent executor framework in place
- SSE live logs streaming to dashboard
- Cost-tracker integrated with DB

### Milestone 4: Compliance & Governance
- Safety-enforcer worker (content moderation + PII scrubbing)
- Audit Dashboard (timeline of crew events)
- RBAC + multi-tenant enforcement

### Milestone 5: Integrations & Exports
- Slack/Notion/Jira integrations
- Export crew.json + logs + compliance reports
- SDKs published (TypeScript client)

### Milestone 6: Testing & Deployment
- Unit, Integration, E2E, Load, Chaos, Security tests
- CI/CD pipelines finalized
- Vercel (FE) + Render/Fly.io (BE)
- Observability: OTel + Sentry dashboards
