---
name: render-deployer
description: Expert in deploying and managing backend applications on Render.com platform with database, cron jobs, and environment management
---

# Render Deployer Skill

**Agent Type:** Backend Deployment Specialist

**Expertise:**
- Render.com platform deployment
- Backend API deployment (FastAPI, Node.js, etc.)
- PostgreSQL database management on Render
- Environment variable configuration
- Custom domains and SSL
- Cron jobs and background workers
- Auto-deploy from GitHub
- Log monitoring and debugging

---

## 🔧 MCP Server Integration

**This skill uses the Render MCP Server for programmatic deployment control.**

### Available MCP Server: `render`

**Configuration:** `.claude/.mcp.json`
```json
{
  "render": {
    "url": "https://mcp.render.com/mcp",
    "headers": {
      "Authorization": "Bearer YOUR_RENDER_API_KEY"
    }
  }
}
```

### MCP Tools Available

When using this skill, you have access to Render MCP tools for:
- ✅ **Deploy services** - Deploy web services, APIs, background workers
- ✅ **Manage databases** - Create and manage PostgreSQL databases
- ✅ **Environment variables** - Set/update environment variables
- ✅ **View logs** - Access deployment and runtime logs
- ✅ **Trigger deploys** - Manual deployment triggers
- ✅ **Service status** - Check service health and status
- ✅ **Custom domains** - Configure custom domains and SSL
- ✅ **Cron jobs** - Schedule background tasks

**Usage Pattern:**
```
User request → Check MCP availability → Use Render MCP tools → Fallback to dashboard instructions
```

---

## 📋 When to Use This Skill

Use `/render-deployer` when:
1. Deploying FastAPI/Flask/Node.js backends to Render
2. Setting up PostgreSQL databases on Render
3. Configuring environment variables
4. Managing cron jobs and background workers
5. Troubleshooting Render deployment issues
6. Setting up auto-deploy from GitHub
7. Configuring custom domains
8. Monitoring service logs and health

---

## 🚀 Common Deployment Workflows

### Workflow 1: Deploy FastAPI Backend
```
1. Create Render account and connect GitHub
2. Create new Web Service on Render
3. Select repository and branch
4. Configure build command: pip install -r requirements.txt
5. Configure start command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
6. Set environment variables (DATABASE_URL, OPENAI_API_KEY, etc.)
7. Deploy and monitor logs
8. Test API endpoints
```

### Workflow 2: Setup PostgreSQL Database
```
1. Create PostgreSQL database on Render
2. Copy Internal Database URL
3. Add DATABASE_URL to web service environment variables
4. Run migrations (Alembic): alembic upgrade head
5. Verify database connection
6. Monitor database metrics
```

### Workflow 3: Configure Auto-Deploy
```
1. Connect GitHub repository to Render service
2. Select branch to auto-deploy (main/production)
3. Enable Auto-Deploy in settings
4. Push to branch → Automatic deployment
5. Monitor build logs
6. Verify deployment success
```

---

## 🔍 Common Commands

### Using Render MCP (Programmatic)
```bash
# MCP handles these operations automatically
"Deploy backend to Render" → Uses MCP deploy_service tool
"Check deployment status" → Uses MCP get_service_status tool
"View logs" → Uses MCP get_logs tool
"Set env var DATABASE_URL" → Uses MCP set_env_var tool
"Create PostgreSQL database" → Uses MCP create_database tool
```

### Using Render Dashboard (Manual)
```
1. Dashboard → New → Web Service
2. Connect GitHub repository
3. Configure:
   - Name: todo-chatbot-backend
   - Region: Oregon (US West)
   - Branch: main
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   - Instance Type: Free (or paid for production)
4. Add Environment Variables
5. Create Service
```

### Using Render CLI (Manual)
```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Deploy
render deploy

# View logs
render logs <service-id>

# List services
render services list
```

---

## 💡 Best Practices

### 1. Build Configuration (render.yaml)
```yaml
services:
  - type: web
    name: todo-chatbot-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: todo-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: JWT_SECRET
        generateValue: true

databases:
  - name: todo-db
    databaseName: todo_chatbot
    user: todo_user
    plan: free
```

### 2. Environment Variables
```bash
# Required for FastAPI backend
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk-...
JWT_SECRET=your-secret-key
CORS_ORIGINS=https://your-frontend.vercel.app

# Use Render's automatic variable
PORT=$PORT  # Render provides this automatically
```

### 3. Health Check Endpoint
```python
# Add to FastAPI app for Render health checks
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 4. Database Migrations
```bash
# Run migrations on deploy using build command
buildCommand: "pip install -r requirements.txt && alembic upgrade head"

# Or use Render's build hooks
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Build Failures
**Symptoms:** Build fails during pip install

**Solutions:**
1. Check Python version in requirements.txt
2. Add runtime.txt: `python-3.11.0`
3. Verify all dependencies are in requirements.txt
4. Check Render build logs via MCP or dashboard

### Issue 2: Service Won't Start
**Symptoms:** Service deployed but not responding

**Solutions:**
1. Verify start command uses `$PORT` variable
2. Check `--host 0.0.0.0` is set (not localhost)
3. View logs via MCP: "Show me the service logs"
4. Check environment variables are set correctly

### Issue 3: Database Connection Issues
**Symptoms:** DATABASE_URL not working

**Solutions:**
1. Use Internal Database URL (not External)
2. Verify DATABASE_URL format: `postgresql://...`
3. Check database is in same region as service
4. Run migrations: add to build command

### Issue 4: CORS Errors
**Symptoms:** Frontend can't connect to backend

**Solutions:**
1. Add frontend URL to CORS_ORIGINS env var
2. Update FastAPI CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔐 Security Best Practices

### Environment Variables
```
✅ Store secrets in Render Environment Variables (not in code)
✅ Use Render's "Generate Value" for JWT_SECRET
✅ Never commit .env files with production secrets
✅ Rotate API keys regularly
✅ Use Internal Database URLs (more secure)
```

### Database Security
```
✅ Use Render's managed PostgreSQL (automatic backups)
✅ Enable SSL connections (default on Render)
✅ Restrict database access to same region
✅ Regular backups (Render handles this)
✅ Use strong database passwords
```

### API Security
```
✅ Enable HTTPS (automatic on Render)
✅ Use JWT authentication
✅ Validate all inputs (Pydantic)
✅ Rate limiting middleware
✅ CORS configuration for specific origins
```

---

## 🎯 Integration with Other Skills

**Works well with:**
- `backend-developer` - Backend implementation
- `database-engineer` - Database schema and migrations
- `deployment-automation` - CI/CD pipeline
- `vercel-deployer` - Frontend deployment coordination
- `github-specialist` - Auto-deploy from GitHub

---

## 📊 Service Types on Render

### 1. Web Service
- **Use for:** FastAPI, Flask, Node.js APIs
- **Features:** Auto-scaling, custom domains, SSL
- **Start command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### 2. Background Worker
- **Use for:** Celery workers, async tasks
- **Features:** Runs continuously, no HTTP endpoint
- **Start command:** `celery -A tasks worker`

### 3. Cron Job
- **Use for:** Scheduled tasks (backups, cleanup)
- **Features:** Runs on schedule, not always-on
- **Schedule:** `0 2 * * *` (daily at 2 AM)

### 4. PostgreSQL Database
- **Use for:** Primary application database
- **Features:** Auto backups, SSL, connection pooling
- **Access:** Internal URL (same region, secure)

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] GitHub repository connected
- [ ] requirements.txt is complete
- [ ] Environment variables identified
- [ ] Database migrations ready
- [ ] Health check endpoint implemented
- [ ] CORS configured for frontend

### During Deployment
- [ ] Service created on Render
- [ ] PostgreSQL database created
- [ ] Environment variables set
- [ ] Build command configured
- [ ] Start command configured
- [ ] Auto-deploy enabled

### Post-Deployment
- [ ] Service status is "Live"
- [ ] Health check responds
- [ ] Database migrations ran
- [ ] API endpoints tested
- [ ] Logs reviewed for errors
- [ ] Frontend connected successfully

---

## ⚡ Quick Reference

### Common MCP Operations
```
"Deploy backend" → MCP deploys service
"Check logs" → MCP retrieves recent logs
"Set env var" → MCP updates environment variable
"Restart service" → MCP triggers restart
"Database status" → MCP checks database health
```

### Render Dashboard URLs
```
Services: https://dashboard.render.com/
Databases: https://dashboard.render.com/databases
Logs: https://dashboard.render.com/web/<service-id>/logs
Settings: https://dashboard.render.com/web/<service-id>/settings
```

---

## 🔄 Continuous Deployment

### Auto-Deploy from GitHub
```
1. Render Dashboard → Service → Settings
2. Enable "Auto-Deploy"
3. Select branch: main
4. On push to main → Automatic deployment
5. Build → Test → Deploy → Live
```

### Manual Deploy
```
Via MCP: "Deploy the backend now"
Via Dashboard: Service → Manual Deploy → Deploy Latest Commit
Via CLI: render deploy
```

---

## 📚 Resources

- **Render Docs:** https://render.com/docs
- **FastAPI Deployment:** https://render.com/docs/deploy-fastapi
- **PostgreSQL on Render:** https://render.com/docs/databases
- **render.yaml Reference:** https://render.com/docs/yaml-spec
- **MCP Configuration:** `.claude/.mcp.json`

---

## 🔐 Security Notes

**⚠️ IMPORTANT:**
- Render MCP requires an API key
- API key stored in `.claude/.mcp.json`
- ❌ Never commit `.mcp.json` to repositories
- ✅ Add `.mcp.json` to `.gitignore`
- ✅ Rotate API keys regularly
- ✅ Use separate keys for dev/staging/production

**API Key Scopes:**
- Full access to account services
- Manage deployments, databases, env vars
- View logs and metrics

---

## 💡 Cost Optimization

### Free Tier Limits
```
- Web Services: 750 hours/month (enough for 1 service 24/7)
- PostgreSQL: 1 free database (90 days, then $7/month)
- Bandwidth: 100 GB/month
- Build minutes: 500 minutes/month
```

### Paid Plans
```
- Starter: $7/month per service
- Standard: $25/month per service (recommended for production)
- Pro: $85/month per service (high traffic)
```

---

**Remember:** Always test backend locally before deploying to Render!
