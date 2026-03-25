# Weather Platform — ECS Fargate Deployment

This directory contains the AWS ECS Fargate deployment configuration for the Weather Platform.

---

## Architecture

The platform runs four services across two tiers behind an Application Load Balancer (ALB):

**Application tier (stateless)**

- `frontend` — Next.js 16 on port 3000
- `backend` — FastAPI on port 8000

**Data tier (stateful — MVP, see Known Limitations)**

- `postgres` — PostgreSQL 16 on port 5432 (application data)
- `timescaledb` — TimescaleDB latest-pg16 on port 5432 (weather metrics)

### ALB Routing

ALB uses path-based routing to direct traffic to the correct target group:

| Rule | Priority | Path pattern | Target group | Port |
| ---- | -------- | ------------ | ------------ | ---- |
| 1    | 10       | `/api/*`     | backend TG   | 8000 |
| 2    | default  | `/*`         | frontend TG  | 3000 |

Health check paths:

- Backend: `GET /health`
- Frontend: `GET /`

---

## Network Configuration

All services run with `awsvpc` network mode. Each task gets its own elastic network interface (ENI) in the VPC.

**Security group rules:**

| Service     | Inbound from           | Port |
| ----------- | ---------------------- | ---- |
| frontend    | ALB security group     | 3000 |
| backend     | ALB security group     | 8000 |
| postgres    | Backend security group | 5432 |
| timescaledb | Backend security group | 5432 |

No service should allow inbound traffic from `0.0.0.0/0` directly.

---

## Secrets Management

All sensitive values are stored in AWS Secrets Manager under the `weather-platform/` prefix. The ECS execution role pulls secrets at task startup — they are never stored in task definitions or environment variables in plaintext.

**Required secrets:**

| Secret path                            | Used by     | Description                   |
| -------------------------------------- | ----------- | ----------------------------- |
| `weather-platform/database-url`        | backend     | PostgreSQL connection string  |
| `weather-platform/timescale-url`       | backend     | TimescaleDB connection string |
| `weather-platform/openweather-api-key` | backend     | OpenWeatherMap API key        |
| `weather-platform/anthropic-api-key`   | backend     | Anthropic Claude API key      |
| `weather-platform/postgres-user`       | postgres    | PostgreSQL username           |
| `weather-platform/postgres-password`   | postgres    | PostgreSQL password           |
| `weather-platform/postgres-db`         | postgres    | PostgreSQL database name      |
| `weather-platform/timescale-user`      | timescaledb | TimescaleDB username          |
| `weather-platform/timescale-password`  | timescaledb | TimescaleDB password          |
| `weather-platform/timescale-db`        | timescaledb | TimescaleDB database name     |

---

## IAM Roles

Two IAM roles are required. Create these before deploying.

### `weather-platform-execution-role`

Assumed by the ECS agent to pull images and inject secrets.

Required policies:

- `AmazonECSTaskExecutionRolePolicy` (AWS managed)
- Inline policy granting `secretsmanager:GetSecretValue` on `arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:weather-platform/*`

### `weather-platform-task-role`

Assumed by running containers for AWS SDK calls.

Required policies:

- `CloudWatchLogsFullAccess` (AWS managed) — for application-level log writes

---

## Pre-Deployment Checklist

Before running `deploy.sh`, verify:

- [ ] AWS CLI configured with sufficient permissions
- [ ] OWM API key has the One Call 3.0 subscription activated
- [ ] All secrets created in AWS Secrets Manager (see table above)
- [ ] ECR repositories created (see ECR Setup below)
- [ ] ECS cluster created (see ECS Cluster Setup below)
- [ ] ALB created with two target groups (backend port 8000, frontend port 3000)
- [ ] ALB listener rules configured (priority 10 for `/api/*`, default for `/*`)
- [ ] Security groups configured per the network table above
- [ ] CloudWatch log groups created: `/ecs/weather-platform-backend`, `/ecs/weather-platform-frontend`, `/ecs/weather-platform-postgres`, `/ecs/weather-platform-timescaledb`
- [ ] Task definition placeholders replaced: `ACCOUNT_ID`, `REGION`, `REPLACE_WITH_ALB_DNS`, `REPLACE_WITH_REGION`

---

## ECR Setup

Create ECR repositories before the first deploy:

```bash
aws ecr create-repository --repository-name weather-platform-backend --region us-east-1
aws ecr create-repository --repository-name weather-platform-frontend --region us-east-1
```

---

## ECS Cluster Setup

```bash
aws ecs create-cluster --cluster-name weather-platform --region us-east-1
```

---

## Registering Task Definitions

After updating placeholder values in the JSON files, register each task definition:

```bash
aws ecs register-task-definition --cli-input-json file://infra/task-definitions/backend.json
aws ecs register-task-definition --cli-input-json file://infra/task-definitions/frontend.json
aws ecs register-task-definition --cli-input-json file://infra/task-definitions/postgres.json
aws ecs register-task-definition --cli-input-json file://infra/task-definitions/timescaledb.json
```

---

## Deploying

From the repository root:

```bash
./infra/deploy.sh us-east-1 123456789012
```

Arguments:

1. `REGION` — AWS region (default: `us-east-1`)
2. `ACCOUNT_ID` — AWS account ID (default: auto-detected via `aws sts get-caller-identity`)

The script:

1. Authenticates Docker to ECR
2. Builds and pushes backend and frontend images
3. Forces new deployments on `backend` and `frontend` ECS services
4. Waits for both services to reach a stable state

---

## Rollback

To roll back to the previous task definition revision:

```bash
# Find the previous revision number
aws ecs describe-task-definition --task-definition weather-platform-backend

# Update the service to the previous revision
aws ecs update-service \
  --cluster weather-platform \
  --service backend \
  --task-definition weather-platform-backend:PREVIOUS_REVISION \
  --region us-east-1
```

Repeat for `frontend` if needed.

---

## Known Limitations (ADR-002)

TimescaleDB and PostgreSQL run as stateful ECS Fargate containers with **no EFS volume mount**. This is an accepted MVP risk:

- Data is lost if the Fargate task is stopped, replaced, or crashes
- This configuration is suitable for E2E testing and demonstration only
- `weather_metrics` data is regenerated on each weather lookup — losing it means re-running the application, not losing business-critical data

**Post-MVP migration path:** Timescale Cloud or RDS Aurora PostgreSQL + TimescaleDB extension. No application code changes are required — only the connection string (`TIMESCALE_URL`) needs updating.

See `docs/adrs/ADR-002-timescaledb-on-ecs-fargate.md` for full decision record.
