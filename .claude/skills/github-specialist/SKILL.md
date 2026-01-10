---
name: github-specialist
description: Full-time equivalent GitHub Specialist agent with expertise in Git workflows, GitHub Actions, code review, and repository management (Digital Agent Factory)
---

# GitHub Specialist Skill

**Agent Type:** Version Control & CI/CD Specialist (Digital Agent Factory)

**Expertise:**
- Git workflows and branching strategies
- GitHub repository management
- GitHub Actions CI/CD pipelines
- Pull request workflows and code review
- Issue management and project boards
- GitHub Secrets and security
- Release management
- Repository automation

---

## 🔧 MCP Server Integration

**This skill uses the GitHub MCP Server for programmatic GitHub operations.**

### Available MCP Server: `github`

**Configuration:** `.claude/.mcp.json`
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
    }
  }
}
```

### MCP Tools Available

When using this skill, you have access to GitHub MCP tools for:
- ✅ **Create/manage repositories** - Initialize repos programmatically
- ✅ **Issues management** - Create, update, close issues
- ✅ **Pull requests** - Create PRs, request reviews, merge
- ✅ **Branch operations** - Create, delete, protect branches
- ✅ **File operations** - Read, write, update repository files
- ✅ **Search repositories** - Find code, issues, PRs
- ✅ **Workflow management** - Trigger GitHub Actions
- ✅ **Release management** - Create and manage releases

**Usage Pattern:**
```
User request → Check MCP availability → Use GitHub MCP tools → Fallback to gh CLI or git commands
```

---

## 📋 When to Use This Skill

Use `/github-specialist` when:
1. Creating or managing GitHub repositories
2. Setting up GitHub Actions workflows
3. Managing pull requests and code reviews
4. Configuring branch protection rules
5. Creating issue/PR templates
6. Managing GitHub Secrets
7. Creating releases and tags
8. Automating GitHub workflows
9. Repository organization and maintenance

---

## 🚀 Common GitHub Workflows

### Workflow 1: Create Pull Request
```
1. Create feature branch: git checkout -b feature/name
2. Make changes and commit
3. Push branch: git push origin feature/name
4. Create PR via MCP or gh CLI
5. Request reviewers
6. Address review comments
7. Merge when approved
```

**Using GitHub MCP:**
```
User: "Create a PR for my changes"
→ MCP creates PR with title, description, reviewers
→ Returns PR URL
```

### Workflow 2: Manage Issues
```
1. Create issue via MCP or gh CLI
2. Add labels (bug, feature, enhancement)
3. Assign to team member
4. Link to project board
5. Track progress
6. Close when resolved
```

### Workflow 3: Setup GitHub Actions CI/CD
```
1. Create .github/workflows/ci.yml
2. Define triggers (push, PR)
3. Configure jobs (test, build, deploy)
4. Add secrets for credentials
5. Test workflow
6. Monitor builds
```

---

## 🔍 Common Commands

### Using GitHub MCP (Programmatic)
```bash
# MCP handles these operations automatically
"Create a PR" → Uses MCP create_pull_request tool
"Close issue #123" → Uses MCP update_issue tool
"Create release v1.0.0" → Uses MCP create_release tool
"Add branch protection to main" → Uses MCP update_branch_protection
```

### Using GitHub CLI (Manual)
```bash
# Pull Requests
gh pr create --title "Add feature" --body "Description"
gh pr list
gh pr view 123
gh pr merge 123

# Issues
gh issue create --title "Bug report" --label bug
gh issue list
gh issue close 123

# Repositories
gh repo create my-repo --public
gh repo view
gh repo clone owner/repo

# Releases
gh release create v1.0.0 --title "Release 1.0.0" --notes "Changes..."

# Secrets
gh secret set SECRET_NAME --body "value"
gh secret list
```

### Using Git Commands
```bash
# Branches
git checkout -b feature/name
git branch -d feature/name
git push origin --delete feature/name

# Commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"

# Tags
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

---

## 💡 Best Practices

### 1. Commit Convention (Conventional Commits)
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Update build process
```

### 2. Branch Naming
```
feature/add-authentication
bugfix/fix-login-error
hotfix/critical-security-patch
release/v1.0.0
```

### 3. Pull Request Template
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Test Plan
How to test these changes

## Screenshots
If applicable
```

### 4. Branch Protection Rules
```
✅ Require PR reviews (minimum 1)
✅ Require status checks to pass
✅ Require branches to be up to date
✅ Enforce for administrators
✅ Restrict force pushes
```

### 5. GitHub Actions Best Practices
```yaml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
```

---

## 🔐 Security Best Practices

### GitHub Secrets Management
```bash
# Add secrets (never hardcode!)
gh secret set OPENAI_API_KEY
gh secret set DATABASE_URL
gh secret set VERCEL_TOKEN

# Use in workflows
${{ secrets.OPENAI_API_KEY }}
```

### Token Permissions
```
✅ Use fine-grained PATs (Personal Access Tokens)
✅ Minimum required scopes only
✅ Set expiration dates
✅ Rotate regularly
✅ Use GitHub Actions GITHUB_TOKEN when possible
```

### Repository Security
```
✅ Enable Dependabot alerts
✅ Enable secret scanning
✅ Enable code scanning (CodeQL)
✅ Require 2FA for organization
✅ Review permissions regularly
```

---

## 🎯 Integration with Other Skills

**Works well with:**
- `vercel-deployer` - Deploy after PR merge
- `deployment-automation` - CI/CD pipeline
- `backend-developer` - Backend PR reviews
- `frontend-developer` - Frontend PR reviews
- `qa-engineer` - Testing in CI/CD

---

## 📚 GitHub Actions Examples

### Example 1: Test and Deploy
```yaml
name: Test and Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

### Example 2: Lint on PR
```yaml
name: Lint
on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: npm run lint
```

---

## 🔄 Release Management

### Semantic Versioning
```
MAJOR.MINOR.PATCH
- MAJOR: Breaking changes (2.0.0)
- MINOR: New features (1.1.0)
- PATCH: Bug fixes (1.0.1)
```

### Release Workflow
```bash
# 1. Update version
npm version patch  # or minor, major

# 2. Create tag
git tag -a v1.0.1 -m "Release 1.0.1"

# 3. Push tag
git push origin v1.0.1

# 4. Create release (via MCP or gh CLI)
gh release create v1.0.1 \
  --title "Version 1.0.1" \
  --notes "Bug fixes and improvements"
```

---

## 📋 Issue & PR Templates

### Bug Report Template
```markdown
---
name: Bug Report
about: Report a bug
labels: bug
---

## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS:
- Browser:
- Version:
```

### Feature Request Template
```markdown
---
name: Feature Request
about: Suggest a new feature
labels: enhancement
---

## Problem
What problem does this solve?

## Solution
Describe the proposed solution

## Alternatives
Alternative solutions considered
```

---

## 📊 Project Board Structure

```
Backlog → To Do → In Progress → In Review → Done
```

**Automation Rules:**
- Issue created → Backlog
- Issue assigned → To Do
- PR opened → In Review
- PR merged → Done
- Issue closed → Done

---

## ⚡ Quick Reference

### Common MCP Operations
```
"Create PR" → MCP handles automatically
"Merge PR #123" → MCP merges with checks
"Create issue" → MCP creates with labels
"Add branch protection" → MCP configures rules
```

### Common gh CLI Operations
```bash
gh pr create        # Create PR
gh pr merge 123     # Merge PR
gh issue create     # Create issue
gh release create   # Create release
```

---

## 🔐 Security Notes

**⚠️ IMPORTANT:**
- GitHub MCP requires a Personal Access Token (PAT)
- Token stored in `.claude/.mcp.json`
- ❌ Never commit `.mcp.json` to repositories
- ✅ Add `.mcp.json` to `.gitignore`
- ✅ Use fine-grained tokens with minimal scopes
- ✅ Rotate tokens every 90 days

**Required Token Scopes:**
- `repo` - Full repository access
- `workflow` - GitHub Actions workflows
- `admin:org` - Organization management (if needed)

---

## 📚 Resources

- **GitHub Docs:** https://docs.github.com/
- **GitHub CLI:** https://cli.github.com/
- **GitHub Actions:** https://docs.github.com/actions
- **Conventional Commits:** https://www.conventionalcommits.org/
- **MCP Configuration:** `.claude/.mcp.json`

---

**Remember:** Always review changes before merging to main/production branches!
