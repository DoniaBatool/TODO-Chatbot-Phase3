# Frontend Development Guide

This directory contains the Next.js frontend application for the Todo Chatbot Phase 3 project.

## Overview

**Technology Stack:**
- Next.js 14 (React framework)
- TypeScript (Type safety)
- Tailwind CSS (Styling)
- shadcn/ui (Component library)
- React Query (Data fetching)
- Vercel (Deployment platform)

## Architecture

### Component-Based Design
- Reusable React components
- TypeScript for type safety
- Tailwind CSS for responsive design
- Client-side state management

### Directory Structure

```
frontend/
├── app/                 # Next.js App Router
│   ├── page.tsx        # Home page
│   ├── layout.tsx      # Root layout
│   └── api/            # API routes (if any)
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   └── features/       # Feature-specific components
├── lib/                # Utilities and helpers
├── hooks/              # Custom React hooks
├── styles/             # Global styles
├── public/             # Static assets
└── package.json        # Dependencies
```

## 🤖 Frontend Specialized Agents (5 Total - EXPANDED!)

These FTE agents are specialized for frontend development tasks:

### Core Frontend Agents (4)

### 1. Frontend Developer (`/frontend-developer`)
**Primary Agent for Frontend Work**

**Skills Available (6):**
- `/sp.frontend-developer` - React/Next.js development
- `/sp.websocket-realtime` - Real-time features (NEW!)
- `/sp.graphql-api` - GraphQL integration (NEW!)
- `/sp.vercel-deployer` - Deploy Next.js apps to Vercel
- `/sp.ab-testing` - A/B testing framework
- `/sp.uiux-designer` - UI/UX design patterns

**Use for:**
- React component development
- Next.js page implementation
- TypeScript integration
- Tailwind CSS styling
- API integration with backend
- Responsive design
- Performance optimization

---

### 2. UI/UX Designer (`/uiux-designer`)
**Design & User Experience Specialist**

**Skills Available (2):**
- `/sp.frontend-developer` - Implement UI designs
- `/sp.ab-testing` - Test design variations

**Use for:**
- User interface design
- Design system creation
- Component library design
- Accessibility (WCAG compliance)
- User flow design
- Wireframing
- Visual hierarchy

---

### 3. Vercel Deployer (`/vercel-deployer`) 🔌 MCP
**Vercel Platform Specialist**

**Skills Available (4):**
- `/sp.vercel-deployer` 🔌 - Vercel deployment (MCP-enhanced)
- `/sp.deployment-automation` - Automated deployments
- `/sp.production-checklist` - Production validation
- `/sp.frontend-developer` - Next.js optimization
- `/sp.performance-logger` - Performance monitoring

**MCP Integration:** ✅ Vercel MCP Server
- Programmatic deployments and status checks
- Environment variable management via API
- Build log access and debugging
- Custom domain configuration
- See `.claude/.mcp.json` for configuration

**Use for:**
- Vercel deployment configuration (automated via MCP)
- Next.js optimization (ISR, SSR, SSG)
- Edge Functions
- Performance optimization
- Core Web Vitals monitoring
- CDN caching
- Troubleshooting deployment issues

---

### 4. QA Engineer (`/qa-engineer`)
**Frontend Testing Specialist**

**Skills Available (3):**
- `/sp.edge-case-tester` - UI edge case testing
- `/sp.ab-testing` - A/B testing framework
- `/sp.production-checklist` - Production validation

**Use for:**
- Component testing (Jest, React Testing Library)
- E2E testing (Playwright, Cypress)
- Accessibility testing
- Performance testing
- Cross-browser testing

---

### 🆕 NEW Frontend Specialist (1)

### 5. Technical Writer (`/technical-writer`)
**Frontend Documentation Specialist**

**Skills Available (3):**
- `/sp.frontend-developer` - Code examples
- `/sp.uiux-designer` - Design system docs
- Component documentation

**Use for:**
- Component library documentation
- User guides and tutorials
- Storybook documentation
- Design system documentation
- Usage examples

---

## 🧠 Frontend Skills Summary (10 Total)

### Core Frontend (3)
- frontend-developer, uiux-designer, vercel-deployer

### Quality & Testing (2)
- edge-case-tester, ab-testing

### 🆕 Modern Frontend (3 NEW!)
- websocket-realtime (Real-time features)
- graphql-api (GraphQL queries)
- feature-flags-management (Feature toggles)

### Deployment & Monitoring (2)
- deployment-automation, performance-logger

---

## 🎯 Common Frontend Workflows

### Workflow 1: Create New Page/Component

```
Pipeline:
1. /uiux-designer → Design UI mockup and component structure
2. /frontend-developer → Implement with React + TypeScript
3. /frontend-developer → Style with Tailwind CSS
4. /qa-engineer → Component tests + accessibility tests
5. /frontend-developer → Integrate with backend API
6. /vercel-deployer → Deploy preview to Vercel
```

**Skills Used:**
- `uiux-designer` - Design patterns
- `frontend-developer` - React implementation
- `edge-case-tester` - UI edge cases
- `vercel-deployer` - Preview deployment

---

### Workflow 2: Implement Design System

```
Pipeline:
1. /uiux-designer → Define design tokens and component library
2. /frontend-developer → Setup shadcn/ui components
3. /uiux-designer → Create component variants
4. /frontend-developer → Implement with TypeScript
5. /qa-engineer → Accessibility testing (WCAG AA)
6. /frontend-developer → Document in Storybook
```

**Skills Used:**
- `uiux-designer` - Design system architecture
- `frontend-developer` - Component implementation
- `edge-case-tester` - Component edge cases
- `ab-testing` - Design variation testing

---

### Workflow 3: Optimize Performance

```
Pipeline:
1. /vercel-deployer → Analyze Core Web Vitals
2. /frontend-developer → Implement code splitting
3. /frontend-developer → Optimize images (next/image)
4. /vercel-deployer → Configure ISR/SSR/SSG
5. /qa-engineer → Performance testing
6. /vercel-deployer → Deploy with optimization
```

**Skills Used:**
- `vercel-deployer` - Performance optimization
- `frontend-developer` - Code optimization
- `performance-logger` - Metrics tracking
- `ab-testing` - Performance A/B tests

---

### Workflow 4: Deploy to Production

```
Pipeline:
1. /qa-engineer → Run E2E tests (Playwright)
2. /qa-engineer → Accessibility audit
3. /frontend-developer → Build production bundle
4. /vercel-deployer → Production checklist validation
5. /vercel-deployer → Deploy to Vercel production
6. /vercel-deployer → Monitor Core Web Vitals
```

**Skills Used:**
- `edge-case-tester` - Comprehensive UI testing
- `production-checklist` - Deployment validation
- `vercel-deployer` - Production deployment
- `performance-logger` - Post-deployment monitoring

---

### Workflow 5: Add A/B Testing

```
Pipeline:
1. /uiux-designer → Design variant A and variant B
2. /frontend-developer → Implement both variants
3. /qa-engineer → Setup A/B testing framework
4. /vercel-deployer → Deploy with feature flags
5. /qa-engineer → Analyze conversion metrics
6. /frontend-developer → Implement winning variant
```

**Skills Used:**
- `ab-testing` - A/B testing framework
- `uiux-designer` - Design variations
- `frontend-developer` - Implementation
- `vercel-deployer` - Feature flag deployment

---

## 📋 Frontend Development Checklist

### For Every New Component:
- [ ] TypeScript types defined
- [ ] Props interface documented
- [ ] Responsive design (mobile-first)
- [ ] Tailwind CSS classes (no inline styles)
- [ ] Accessibility (ARIA labels, keyboard navigation)
- [ ] Error states handled
- [ ] Loading states handled
- [ ] Component tests written
- [ ] Storybook story created (if applicable)

### For Every New Page:
- [ ] SEO metadata (title, description)
- [ ] OpenGraph tags for social sharing
- [ ] Responsive layout (mobile, tablet, desktop)
- [ ] Loading skeleton implemented
- [ ] Error boundary implemented
- [ ] API integration with error handling
- [ ] Performance optimized (lazy loading, code splitting)
- [ ] Accessibility tested (keyboard, screen reader)

### For Styling:
- [ ] Tailwind CSS utility classes used
- [ ] No hardcoded colors (use design tokens)
- [ ] Consistent spacing (use spacing scale)
- [ ] Consistent typography (use text scale)
- [ ] Dark mode support (if applicable)
- [ ] Responsive breakpoints (sm, md, lg, xl)
- [ ] Hover/focus states defined
- [ ] Touch-friendly targets (min 44x44px)

### For Performance:
- [ ] Images optimized (next/image)
- [ ] Code splitting implemented
- [ ] Lazy loading for heavy components
- [ ] Bundle size analyzed
- [ ] Core Web Vitals measured (LCP, FID, CLS)
- [ ] Lighthouse score > 90
- [ ] No unnecessary re-renders
- [ ] Memoization where needed

### For Accessibility:
- [ ] WCAG AA compliance minimum
- [ ] Semantic HTML used
- [ ] ARIA labels where needed
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast ratio ≥ 4.5:1
- [ ] Screen reader tested
- [ ] Form labels associated

### For Production:
- [ ] Environment variables configured
- [ ] Build succeeds without errors
- [ ] No console errors in browser
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Mobile tested (iOS, Android)
- [ ] E2E tests passing
- [ ] Performance budget met
- [ ] Analytics configured

---

## 🔧 Frontend Skills Reference

### Core Frontend Skills (3)
1. `/sp.frontend-developer` - React/Next.js implementation
2. `/sp.uiux-designer` - Design patterns and systems
3. `/sp.vercel-deployer` - Vercel deployment and optimization

### Testing & Quality Skills (2)
1. `/sp.edge-case-tester` - UI edge case testing
2. `/sp.ab-testing` - A/B testing framework

### Production & Deployment Skills (3)
1. `/sp.deployment-automation` - CI/CD automation
2. `/sp.production-checklist` - Deployment validation
3. `/sp.performance-logger` - Performance monitoring

---

## 🏗️ Frontend Best Practices

### 1. Component Design
- ✅ Single Responsibility Principle
- ✅ Reusable and composable
- ✅ Typed with TypeScript
- ✅ Props interface documented
- ✅ Default props defined

### 2. State Management
- ✅ React Query for server state
- ✅ Context API for global UI state
- ✅ Local state with useState
- ✅ Avoid prop drilling
- ✅ Memoize expensive computations

### 3. Styling
- ✅ Tailwind utility classes
- ✅ Design tokens for consistency
- ✅ Mobile-first responsive design
- ✅ No inline styles
- ✅ Component variants with CVA

### 4. Performance
- ✅ next/image for images
- ✅ Dynamic imports for code splitting
- ✅ React.memo for expensive components
- ✅ useCallback/useMemo where needed
- ✅ Virtualization for long lists

### 5. Accessibility
- ✅ Semantic HTML elements
- ✅ ARIA labels and roles
- ✅ Keyboard navigation support
- ✅ Focus management
- ✅ Screen reader compatibility

### 6. Type Safety
- ✅ TypeScript strict mode
- ✅ Interface for component props
- ✅ API response types defined
- ✅ Avoid `any` type
- ✅ Use discriminated unions

---

## 🚀 Quick Start

### Development Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your values

# Start development server
npm run dev
# Open http://localhost:3000
```

### Running Tests
```bash
# Unit/Component tests (Jest + React Testing Library)
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Accessibility tests
npm run test:a11y

# With coverage
npm run test:coverage
```

### Building for Production
```bash
# Build production bundle
npm run build

# Test production build locally
npm run start

# Analyze bundle size
npm run analyze
```

### Linting & Formatting
```bash
# ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Prettier
npm run format
```

---

## 🎨 Design System

### Typography Scale
```typescript
// Tailwind CSS classes
text-xs    // 12px
text-sm    // 14px
text-base  // 16px
text-lg    // 18px
text-xl    // 20px
text-2xl   // 24px
text-3xl   // 30px
text-4xl   // 36px
```

### Color Palette
```typescript
// Primary colors
primary: {
  50: '#eff6ff',
  500: '#3b82f6',
  900: '#1e3a8a',
}

// Use in Tailwind:
// bg-primary-500
// text-primary-900
// border-primary-50
```

### Spacing Scale
```typescript
// Tailwind spacing (rem)
space-1  // 0.25rem (4px)
space-2  // 0.5rem (8px)
space-4  // 1rem (16px)
space-6  // 1.5rem (24px)
space-8  // 2rem (32px)
space-12 // 3rem (48px)
```

### Component Variants
```typescript
// Example: Button variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// With sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
```

---

## 🧪 Testing Strategy

### Unit/Component Tests (Jest + RTL)
```typescript
// Example component test
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

test('button click handler works', async () => {
  const handleClick = jest.fn()
  render(<Button onClick={handleClick}>Click me</Button>)

  await userEvent.click(screen.getByRole('button'))

  expect(handleClick).toHaveBeenCalledTimes(1)
})
```

### E2E Tests (Playwright)
```typescript
// Example E2E test
test('user can create a todo', async ({ page }) => {
  await page.goto('/')
  await page.fill('[placeholder="Add new task"]', 'Buy milk')
  await page.click('button:has-text("Add")')

  await expect(page.locator('text=Buy milk')).toBeVisible()
})
```

### Accessibility Tests
```typescript
// Example accessibility test
import { axe, toHaveNoViolations } from 'jest-axe'

test('page has no accessibility violations', async () => {
  const { container } = render(<HomePage />)
  const results = await axe(container)

  expect(results).toHaveNoViolations()
})
```

---

## 📊 Performance Metrics

### Core Web Vitals Targets
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Lighthouse Score Targets
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 95
- SEO: > 90

### Bundle Size Targets
- First Load JS: < 200 KB
- Route JS: < 100 KB per route
- Image optimization: WebP/AVIF format

---

## 📚 Additional Resources

- **Root CLAUDE.md**: Project-wide guidelines and all agents
- **Backend CLAUDE.md**: `../backend/CLAUDE.md` for backend-specific guides
- **Constitution**: `.specify/memory/constitution.md` for project principles
- **Next.js Docs**: https://nextjs.org/docs
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com
- **Skills Directory**: `../.claude/skills/` for all reusable skills
- **Agents Directory**: `../.claude/agents/` for all FTE agents

---

## 🎯 Remember

**Before implementing ANY frontend feature:**
1. ✅ Check which agents apply
2. ✅ Check which skills apply
3. ✅ Display skill plan in terminal
4. ✅ Wait for user approval
5. ✅ Execute using identified skills

**Skills are MANDATORY - not optional!**

Manual implementation when skill exists = VIOLATION of project guidelines.

---

## 🔄 Integration with Backend

### API Communication
```typescript
// Example: Fetching tasks from backend
import { useQuery } from '@tanstack/react-query'

const useTasks = () => {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await fetch('/api/tasks', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      return response.json()
    },
  })
}
```

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Authentication Flow
1. User logs in → Backend returns JWT
2. Store JWT in localStorage/sessionStorage
3. Include JWT in Authorization header for API calls
4. Refresh token before expiration

---

**Frontend Development** - Powered by Reusable Intelligence 🚀
