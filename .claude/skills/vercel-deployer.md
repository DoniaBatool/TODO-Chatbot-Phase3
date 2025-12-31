---
description: Full-time equivalent Vercel Specialist agent with expertise in Vercel deployment, Edge Functions, ISR, and performance optimization (Digital Agent Factory)
---

## Professional Profile

**Role**: Vercel Deployment Specialist (FTE Digital Employee)
**Expertise**: Vercel deployment, Next.js optimization, Edge Functions, Analytics
**Experience**: 3+ years equivalent

## Vercel Deployment Workflow

### 1. Project Setup

**vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "DATABASE_URL": "@database-url"
  },
  "build": {
    "env": {
      "NEXT_TELEMETRY_DISABLED": "1"
    }
  }
}
```

### 2. Environment Variables

**Production Secrets:**
```bash
# Add via Vercel CLI
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://api.example.com

vercel env add DATABASE_URL production
# Enter: postgresql://...

# Preview/Development
vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_API_URL development
```

**next.config.mjs:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Environment variables validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // Image optimization
  images: {
    domains: ['api.example.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains',
          },
        ],
      },
    ];
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },

  // Rewrites (API proxy)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.example.com/api/:path*',
      },
    ];
  },
};

export default nextConfig;
```

### 3. Deploy Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs <deployment-url>

# Inspect deployment
vercel inspect <deployment-url>
```

### 4. Incremental Static Regeneration (ISR)

```typescript
// app/tasks/page.tsx
export const revalidate = 60; // Revalidate every 60 seconds

export default async function TasksPage() {
  const tasks = await fetch('https://api.example.com/api/tasks', {
    next: { revalidate: 60 }
  }).then(res => res.json());

  return (
    <div>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
}
```

### 5. Edge Functions

**Middleware:**
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Get token from cookie
  const token = request.cookies.get('auth-token')?.value;

  // Redirect to login if not authenticated
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add custom header
  const response = NextResponse.next();
  response.headers.set('x-custom-header', 'value');

  return response;
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

**Edge API Route:**
```typescript
// app/api/edge-example/route.ts
export const runtime = 'edge';

export async function GET(request: Request) {
  return Response.json({ message: 'Hello from Edge' });
}
```

### 6. Performance Optimization

**Image Optimization:**
```typescript
import Image from 'next/image';

export function ProductCard({ product }) {
  return (
    <div>
      <Image
        src={product.image}
        alt={product.name}
        width={400}
        height={300}
        priority={false}  // Lazy load
        placeholder="blur"
        blurDataURL={product.blurImage}
      />
    </div>
  );
}
```

**Font Optimization:**
```typescript
import { Inter, Roboto_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto-mono',
});

export default function RootLayout({ children }) {
  return (
    <html className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

**Code Splitting:**
```typescript
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

### 7. Vercel Analytics

**Setup:**
```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 8. Custom Domains

```bash
# Add domain
vercel domains add example.com

# Add www redirect
vercel domains add www.example.com --redirect example.com

# Check DNS
vercel dns ls

# Remove domain
vercel domains rm example.com
```

### 9. Deployment Hooks

**GitHub Integration:**
```yaml
# .github/workflows/vercel-preview.yml
name: Vercel Preview Deployment

on:
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          scope: ${{ secrets.VERCEL_ORG_ID }}
```

### 10. Monitoring

**Vercel Dashboard Metrics:**
- Deployment frequency
- Build time
- Error rate
- Traffic analytics
- Core Web Vitals
- Edge Function usage

**Alerts:**
- Failed deployments
- High error rate
- Performance degradation

## Deliverables

- [ ] Vercel project configured
- [ ] Environment variables set
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Analytics enabled
- [ ] ISR configured
- [ ] Edge Functions deployed
- [ ] Performance optimized
- [ ] Monitoring alerts set

## References

- Vercel Docs: https://vercel.com/docs
- Next.js Deployment: https://nextjs.org/docs/deployment
- Edge Functions: https://vercel.com/docs/functions/edge-functions
