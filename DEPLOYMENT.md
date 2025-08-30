# Deployment Guide

This guide covers deploying the AI User-Customizable Crew Platform to various environments.

## Quick Deploy Options

### Option 1: Vercel (Frontend) + Render (Backend) - Recommended

**Frontend to Vercel:**
1. Connect your GitHub repository to Vercel
2. Set build command: `cd apps/frontend && npm run build`
3. Set output directory: `apps/frontend/.next`
4. Add environment variables:
   - `NEXT_PUBLIC_API_BASE_URL`: Your backend URL

**Backend to Render:**
1. Connect your GitHub repository to Render
2. Use the included `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Deploy automatically on git push

### Option 2: Fly.io (Backend) + Vercel (Frontend)

**Backend to Fly.io:**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login and create app
fly auth login
fly launch --config fly.toml

# Set secrets
fly secrets set OPENAI_API_KEY=your_key
fly secrets set DATABASE_URL=your_db_url
fly secrets set JWT_SECRET=your_secret

# Deploy
fly deploy
```

### Option 3: Self-Hosted with Docker

```bash
# Clone repository
git clone <your-repo-url>
cd ai-user-customizable-crew

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start production stack
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# AI APIs (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Security
JWT_SECRET=your-secure-random-string

# Storage (optional but recommended)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET=your-bucket-name
```

### Optional Integration Variables

```bash
# Slack Integration
SLACK_BOT_TOKEN=xoxb-...

# Notion Integration
NOTION_TOKEN=secret_...
NOTION_DATABASE_ID=your-database-id
NOTION_TEMPLATES_DATABASE_ID=your-templates-db-id

# Jira Integration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-token

# Redis & NATS (if external)
REDIS_URL=redis://host:port
NATS_URL=nats://host:port
```

## Database Setup

### Managed Database (Recommended)

**Render PostgreSQL:**
- Automatically configured via `render.yaml`
- Includes automated backups
- SSL enabled by default

**Fly.io PostgreSQL:**
```bash
fly postgres create --name ai-crew-db
fly postgres attach ai-crew-db
```

**Other Providers:**
- AWS RDS
- Google Cloud SQL
- Azure Database
- PlanetScale
- Supabase

### Self-Hosted Database

```bash
# Using Docker
docker run -d \
  --name ai-crew-postgres \
  -e POSTGRES_DB=ai_crew_production \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15
```

## SSL/TLS Configuration

### Automatic SSL (Recommended)

**Vercel:** Automatic SSL for custom domains
**Render:** Automatic SSL certificates
**Fly.io:** Automatic SSL with custom domains

### Manual SSL (Self-Hosted)

1. Obtain SSL certificates (Let's Encrypt recommended):
```bash
# Using Certbot
sudo certbot certonly --standalone -d yourdomain.com
```

2. Update `nginx.conf` with certificate paths:
```nginx
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

## Monitoring & Observability

### Health Checks

All deployment options include health check endpoints:
- `/health` - Basic health check
- `/health/ready` - Readiness check with dependencies

### Logging

**Production Logging:**
- Structured JSON logs
- Error tracking with Sentry (configure `SENTRY_DSN`)
- Performance monitoring

**Log Aggregation:**
- Render: Built-in log aggregation
- Fly.io: Fly logs integration
- Self-hosted: Consider ELK stack or Grafana Loki

### Metrics

**Application Metrics:**
- API response times
- Job execution metrics
- Cost tracking
- Safety score monitoring

**Infrastructure Metrics:**
- CPU/Memory usage
- Database performance
- Redis performance

## Scaling Considerations

### Horizontal Scaling

**API Scaling:**
- Stateless design allows easy horizontal scaling
- Use load balancer for multiple instances
- Consider Redis for session storage if needed

**Database Scaling:**
- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer recommended)
- Consider database sharding for very large deployments

**Background Workers:**
- Separate worker processes for crew execution
- Use NATS for job queuing
- Scale workers independently based on load

### Performance Optimization

**Frontend:**
- CDN for static assets (Vercel includes this)
- Image optimization
- Code splitting and lazy loading

**Backend:**
- Database query optimization
- Caching with Redis
- API response caching
- Async processing for long-running tasks

## Security Checklist

### Application Security

- [ ] Environment variables properly configured
- [ ] JWT secrets are strong and unique
- [ ] API rate limiting enabled
- [ ] Input validation and sanitization
- [ ] PII scrubbing enabled
- [ ] HTTPS enforced
- [ ] CORS properly configured

### Infrastructure Security

- [ ] Database access restricted
- [ ] Redis access secured
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting setup

### Compliance

- [ ] Data retention policies
- [ ] Audit logging enabled
- [ ] PII handling procedures
- [ ] Access control (RBAC)
- [ ] Regular security assessments

## Backup & Recovery

### Database Backups

**Automated Backups:**
- Render: Daily automated backups
- Fly.io: Configure backup schedule
- Self-hosted: Use `pg_dump` with cron

**Manual Backup:**
```bash
# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql $DATABASE_URL < backup_file.sql
```

### Application Data

**File Storage Backups:**
- S3: Cross-region replication
- Local storage: Regular file system backups

**Configuration Backups:**
- Export crew configurations regularly
- Version control for infrastructure code
- Document environment variables

## Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Check connection pool
# Monitor active connections in database
```

**API Performance Issues:**
```bash
# Check API health
curl https://your-api-url/health

# Monitor response times
# Check database query performance
```

**Frontend Build Issues:**
```bash
# Clear Next.js cache
rm -rf apps/frontend/.next

# Rebuild
cd apps/frontend && npm run build
```

### Logs and Debugging

**API Logs:**
```bash
# Render
render logs --service ai-crew-api

# Fly.io
fly logs

# Docker
docker logs ai-crew-api
```

**Database Logs:**
```bash
# Check slow queries
# Monitor connection counts
# Review error logs
```

## Support

For deployment issues:
1. Check the troubleshooting section above
2. Review application logs
3. Verify environment variables
4. Test database connectivity
5. Check external service integrations

For additional support, please refer to the project documentation or create an issue in the repository.
