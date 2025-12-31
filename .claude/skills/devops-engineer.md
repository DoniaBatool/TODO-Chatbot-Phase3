---
description: Full-time equivalent DevOps Engineer agent with expertise in CI/CD, Docker, infrastructure, monitoring, and automation (Digital Agent Factory)
---

## Professional Profile

**Role**: Senior DevOps Engineer (FTE Digital Employee)
**Expertise**: CI/CD, Docker, Kubernetes, Infrastructure as Code, Monitoring
**Experience**: 5+ years equivalent

## Core Competencies

- CI/CD Pipelines (GitHub Actions, GitLab CI)
- Containerization (Docker, Docker Compose)
- Orchestration (Kubernetes, Docker Swarm)
- Infrastructure as Code (Terraform, Pulumi)
- Monitoring & Logging (Prometheus, Grafana, ELK)
- Cloud Platforms (AWS, GCP, Azure, Fly.io)
- Scripting (Bash, Python, Terraform)

## CI/CD Pipeline Setup

### GitHub Actions Workflow

**.github/workflows/ci-cd.yml:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  # Frontend Tests
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run type check
        run: |
          cd frontend
          npm run type-check

      - name: Run lint
        run: |
          cd frontend
          npm run lint

      - name: Run unit tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/lcov.info
          flags: frontend

  # Backend Tests
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend

  # E2E Tests
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [frontend-tests, backend-tests]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install Playwright
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/

  # Deploy to Staging
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    needs: [frontend-tests, backend-tests, e2e-tests]
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Deploy frontend to Vercel
        run: |
          cd frontend
          npx vercel --token=${{ secrets.VERCEL_TOKEN }} --yes

      - name: Deploy backend to Fly.io
        run: |
          cd backend
          flyctl deploy --app todo-chatbot-staging
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

  # Deploy to Production
  deploy-production:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    needs: [frontend-tests, backend-tests, e2e-tests]
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy frontend to Vercel
        run: |
          cd frontend
          npx vercel --prod --token=${{ secrets.VERCEL_TOKEN }} --yes

      - name: Deploy backend to Fly.io
        run: |
          cd backend
          flyctl deploy --app todo-chatbot-prod
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      - name: Run smoke tests
        run: |
          curl -f https://api.example.com/api/health || exit 1
```

## Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application
COPY . .

# Run migrations and start server
CMD poetry run alembic upgrade head && \
    poetry run uvicorn src.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 4
```

**docker-compose.yml (Development):**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopass
      POSTGRES_DB: tododb
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://todouser:todopass@postgres:5432/tododb
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

volumes:
  postgres-data:
```

## Monitoring Setup

**Prometheus Config:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

**Application Metrics (FastAPI):**
```python
from prometheus_client import Counter, Histogram, make_asgi_app
from fastapi import FastAPI

app = FastAPI()

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# Metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

## Infrastructure as Code

**Terraform (AWS Example):**
```hcl
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "todo-chatbot-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "todo-chatbot-cluster"
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier             = "todo-chatbot-db"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_encrypted      = true
  username               = var.db_username
  password               = var.db_password
  db_name                = "tododb"
  skip_final_snapshot    = false
  final_snapshot_identifier = "todo-chatbot-final"

  tags = {
    Name = "todo-chatbot-db"
  }
}
```

## Deliverables

- [ ] CI/CD pipeline configured
- [ ] Docker images built and tested
- [ ] Infrastructure as Code (Terraform/Pulumi)
- [ ] Monitoring setup (Prometheus + Grafana)
- [ ] Logging aggregation (ELK/Loki)
- [ ] Alerting rules configured
- [ ] Backup and recovery procedures
- [ ] Disaster recovery plan
- [ ] Runbooks for common operations

## References

- GitHub Actions: https://docs.github.com/actions
- Docker: https://docs.docker.com/
- Kubernetes: https://kubernetes.io/docs/
- Terraform: https://www.terraform.io/docs
