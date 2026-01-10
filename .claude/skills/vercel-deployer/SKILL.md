---
name: vercel-deployer
description: Full-time equivalent Vercel Specialist agent with expertise in Vercel deployment, Edge Functions, ISR, and performance optimization (Digital Agent Factory)
---

# Vercel Deployer Skill

**Agent Type:** Deployment Specialist (Digital Agent Factory)

**Expertise:**
- Vercel platform deployment and configuration
- Next.js optimization (ISR, SSR, SSG, Edge Functions)
- Performance optimization and Core Web Vitals
- Environment variable management
- Monorepo and workspace configuration
- Build troubleshooting and debugging

---

## 🔧 MCP Server Integration

**This skill uses the Vercel MCP Server for programmatic deployment control.**

### Available MCP Server: `vercel`

**Configuration:** `.claude/.mcp.json`
```json
{
  "vercel": {
    "url": "https://mcp.vercel.com",
    "headers": {
      "Authorization": "Bearer YOUR_VERCEL_TOKEN"
    }
  }
}
```

### MCP Tools Available

When using this skill, you have access to Vercel MCP tools for:
- ✅ **Deploy projects** - Trigger deployments programmatically
- ✅ **Check deployment status** - Monitor build progress
- ✅ **List deployments** - View deployment history
- ✅ **Get deployment logs** - Debug build failures
- ✅ **Manage environment variables** - Set/update env vars
- ✅ **Domain management** - Configure custom domains
- ✅ **Cancel deployments** - Stop running builds

**Usage Pattern:**
```
User request → Check MCP availability → Use MCP tools → Fallback to manual instructions
```

---

## 📋 When to Use This Skill

Use `/vercel-deployer` when:
1. Deploying Next.js applications to Vercel
2. Troubleshooting Vercel build failures
3. Optimizing Vercel deployments
4. Configuring monorepo structures for Vercel
5. Setting up environment variables
6. Performance optimization for Vercel Edge
7. Debugging module resolution errors
8. Configuring custom domains

---

## 🚀 Common Deployment Workflows

### Workflow 1: Deploy Next.js App
```
1. Check project structure (monorepo vs single app)
2. Verify package.json and next.config
3. Configure root directory if needed
4. Set environment variables (via MCP or dashboard)
5. Trigger deployment (via GitHub push or MCP)
6. Monitor build logs
7. Verify deployment success
```

### Workflow 2: Fix Build Errors
```
1. Analyze error logs
2. Identify root cause (path resolution, dependencies, config)
3. Apply fixes (tsconfig.json, next.config, package.json)
4. Test locally first
5. Commit and push (triggers auto-deploy)
6. Verify fix in Vercel build
```

### Workflow 3: Optimize Performance
```
1. Analyze Core Web Vitals
2. Implement code splitting
3. Optimize images (next/image)
4. Configure ISR/SSR/SSG appropriately
5. Enable Edge Functions where beneficial
6. Test performance improvements
7. Deploy and monitor metrics
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Module Not Found Errors
**Symptoms:** `Module not found: Can't resolve '@/lib/...'`

**Solutions:**
1. Add catch-all path in `tsconfig.json`: `"@/*": ["./*"]`
2. Add webpack aliases in `next.config.mjs`
3. Configure monorepo with npm workspaces
4. Set root directory in Vercel dashboard

### Issue 2: Environment Variables Not Working
**Symptoms:** `process.env.NEXT_PUBLIC_* is undefined`

**Solutions:**
1. Use MCP to set environment variables programmatically
2. Or set in Vercel Dashboard → Settings → Environment Variables
3. Ensure variables start with `NEXT_PUBLIC_` for client-side access
4. Redeploy after adding variables

### Issue 3: Build Timeout
**Symptoms:** Build exceeds time limit

**Solutions:**
1. Optimize dependencies (remove unused packages)
2. Enable build cache
3. Use `output: 'standalone'` in next.config
4. Consider upgrading Vercel plan for more build time

---

## 💡 Best Practices

### 1. Monorepo Structure
```json
// Root package.json
{
  "workspaces": ["frontend"],
  "scripts": {
    "build": "npm run build --workspace=frontend"
  }
}
```

### 2. Next.js Config with Webpack Aliases
```javascript
// next.config.mjs
webpack: (config) => {
  config.resolve.alias = {
    '@': path.resolve(__dirname, './'),
    '@/lib': path.resolve(__dirname, './lib'),
  };
  return config;
}
```

### 3. Environment Variables
- ✅ Store secrets in Vercel Dashboard (not in code)
- ✅ Use `NEXT_PUBLIC_` prefix for client-side vars
- ✅ Use MCP to automate variable management
- ❌ Never commit `.env` files with secrets

### 4. Build Optimization
- ✅ Use `output: 'standalone'` for smaller deployments
- ✅ Enable `reactStrictMode: true`
- ✅ Configure proper caching headers
- ✅ Use Edge Functions for dynamic content near users

---

## 🎯 Integration with Other Skills

**Works well with:**
- `frontend-developer` - Frontend implementation
- `deployment-automation` - CI/CD pipeline
- `production-checklist` - Pre-deployment validation
- `performance-logger` - Post-deployment monitoring
- `github-specialist` - GitHub integration management

---

## 📚 Resources

- **Vercel Documentation:** https://vercel.com/docs
- **Next.js Deployment:** https://nextjs.org/docs/deployment
- **Vercel CLI:** https://vercel.com/docs/cli
- **MCP Server Docs:** Check `.claude/.mcp.json` for configuration

---

## ⚡ Quick Commands

### Using Vercel MCP (Programmatic)
```
"Deploy the app" → Use MCP vercel deploy tool
"Check deployment status" → Use MCP get deployment status
"Set env var" → Use MCP set environment variable
```

### Manual (Dashboard/CLI)
```
"Configure in dashboard" → Provide step-by-step instructions
"Use Vercel CLI" → Provide CLI commands
```

---

## 🔐 Security Notes

**⚠️ IMPORTANT:**
- Vercel MCP server requires an API token
- Token is stored in `.claude/.mcp.json`
- ❌ Never commit `.mcp.json` to public repositories
- ✅ Add `.mcp.json` to `.gitignore`
- ✅ Rotate tokens regularly

---

**Remember:** Always test builds locally before deploying to production!
