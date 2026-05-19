# CLAUDE.md — Next.js 15 + SQLite SaaS Project

**Opinionated, production-ready context for Claude Code.**

---

## Stack & Versions

- **Next.js:** 15.x (App Router only, no Pages Router)
- **React:** 19.x (Server Components by default)
- **TypeScript:** 5.x (strict mode)
- **Database:** SQLite via `better-sqlite3` or Turso
- **ORM:** Drizzle ORM (type-safe, zero runtime overhead)
- **Auth:** NextAuth.js v5 (App Router compatible)
- **Styling:** Tailwind CSS 4.x
- **Deployment:** Vercel (or any Node.js host)

---

## Project Structure

```
/
├── app/                    # Next.js 15 App Router
│   ├── (auth)/            # Auth routes (login, signup)
│   ├── (dashboard)/       # Protected dashboard routes
│   ├── api/               # API routes
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── components/
│   ├── ui/                # Shadcn/ui components
│   └── features/          # Feature-specific components
├── lib/
│   ├── db/
│   │   ├── schema.ts      # Drizzle schema
│   │   ├── client.ts      # Database client
│   │   └── migrations/    # SQL migration files
│   ├── auth.ts            # NextAuth config
│   └── utils.ts           # Shared utilities
├── public/                # Static assets
├── drizzle.config.ts      # Drizzle ORM config
├── next.config.ts         # Next.js config
├── tailwind.config.ts     # Tailwind config
└── tsconfig.json          # TypeScript config
```

---

## Naming Conventions

### Files & Folders

- **Routes:** lowercase with hyphens (`/user-settings`, not `/userSettings`)
- **Components:** PascalCase (`UserProfile.tsx`, not `user-profile.tsx`)
- **Utilities:** camelCase (`formatDate.ts`, not `format-date.ts`)
- **Route groups:** parentheses for layout grouping (`(auth)`, `(dashboard)`)

### Code

- **React Server Components:** default (no `"use client"` unless needed)
- **Client Components:** explicit `"use client"` at top of file
- **Database tables:** snake_case (`user_profiles`, not `userProfiles`)
- **TypeScript types:** PascalCase with `T` prefix for generic types (`TUser`, `TPost`)

---

## Database & Migrations

### Schema Definition

Use Drizzle ORM schema in `lib/db/schema.ts`:

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  email: text('email').notNull().unique(),
  name: text('name'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull(),
});
```

### Migration Rules

1. **Never edit existing migrations** — create a new one
2. **Always use timestamps** — `YYYYMMDDHHMMSS_description.sql`
3. **Test migrations locally** before committing
4. **Rollback plan required** for destructive changes (DROP, ALTER)
5. **No raw SQL in application code** — use Drizzle queries

### Running Migrations

```bash
# Generate migration from schema changes
npm run db:generate

# Apply migrations
npm run db:migrate

# Push schema directly (dev only)
npm run db:push
```

---

## Component Patterns

### Server Components (Default)

```typescript
// app/dashboard/page.tsx
import { db } from '@/lib/db/client';
import { users } from '@/lib/db/schema';

export default async function DashboardPage() {
  const allUsers = await db.select().from(users);
  return <div>{/* render */}</div>;
}
```

### Client Components (Interactive)

```typescript
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### Server Actions (Form Handling)

```typescript
// app/actions.ts
'use server';

import { db } from '@/lib/db/client';
import { users } from '@/lib/db/schema';
import { revalidatePath } from 'next/cache';

export async function createUser(formData: FormData) {
  const email = formData.get('email') as string;
  await db.insert(users).values({ email, createdAt: new Date() });
  revalidatePath('/dashboard');
}
```

---

## API Routes

### REST Endpoints

```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { users } from '@/lib/db/schema';

export async function GET() {
  const allUsers = await db.select().from(users);
  return NextResponse.json(allUsers);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newUser = await db.insert(users).values(body).returning();
  return NextResponse.json(newUser[0], { status: 201 });
}
```

### Error Handling

```typescript
try {
  // operation
} catch (error) {
  console.error('Operation failed:', error);
  return NextResponse.json(
    { error: 'Internal server error' },
    { status: 500 }
  );
}
```

---

## Authentication

### NextAuth.js v5 Setup

```typescript
// lib/auth.ts
import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { db } from '@/lib/db/client';
import { users } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      authorize: async (credentials) => {
        const user = await db
          .select()
          .from(users)
          .where(eq(users.email, credentials.email as string))
          .get();
        if (!user) return null;
        // verify password (use bcrypt in production)
        return user;
      },
    }),
  ],
});
```

### Protected Routes

```typescript
// app/(dashboard)/layout.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session) redirect('/login');
  return <div>{children}</div>;
}
```

---

## Dev Commands

```bash
# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Database operations
npm run db:generate    # Generate migration from schema
npm run db:migrate     # Apply migrations
npm run db:push        # Push schema (dev only)
npm run db:studio      # Open Drizzle Studio

# Build & deploy
npm run build
npm run start
```

---

## What We Don't Do (And Why)

### ❌ No Pages Router

**Why:** App Router is the future. Pages Router is legacy. Mixing them creates confusion.

### ❌ No Prisma

**Why:** Drizzle is faster, lighter, and more type-safe. Prisma's runtime overhead is unnecessary for SQLite.

### ❌ No `any` types

**Why:** TypeScript strict mode catches bugs. `any` defeats the purpose.

### ❌ No inline styles

**Why:** Tailwind utility classes are faster and more maintainable than CSS-in-JS.

### ❌ No `useEffect` for data fetching

**Why:** Server Components fetch data at build/request time. Client-side fetching is slower and more complex.

### ❌ No manual SQL strings

**Why:** Drizzle provides type-safe queries. Raw SQL is error-prone and hard to refactor.

### ❌ No environment variables in client components

**Why:** `NEXT_PUBLIC_*` vars are exposed to the browser. Keep secrets server-side only.

### ❌ No default exports for components

**Why:** Named exports are easier to refactor and tree-shake. Exception: Next.js page/layout files.

---

## Performance Rules

1. **Server Components by default** — only use `"use client"` when you need interactivity
2. **Streaming with Suspense** — wrap slow components in `<Suspense>` with fallback
3. **Image optimization** — always use `next/image`, never `<img>`
4. **Font optimization** — use `next/font` for Google Fonts
5. **Database indexes** — add indexes for frequently queried columns
6. **Edge runtime** — use `export const runtime = 'edge'` for API routes when possible

---

## Security Checklist

- [ ] All user inputs validated (Zod schemas)
- [ ] SQL injection prevented (Drizzle parameterized queries)
- [ ] XSS prevented (React escapes by default, but sanitize HTML if needed)
- [ ] CSRF tokens for mutations (NextAuth handles this)
- [ ] Rate limiting on API routes (use `@upstash/ratelimit`)
- [ ] Environment variables never exposed to client
- [ ] Database credentials in `.env.local` (never committed)

---

## Testing Strategy

- **Unit tests:** Vitest for utilities and pure functions
- **Integration tests:** Playwright for critical user flows
- **Type safety:** TypeScript strict mode (no `any`, no implicit `any`)
- **Manual QA:** Test on mobile viewport (Tailwind responsive classes)

---

## Deployment Checklist

- [ ] `npm run build` succeeds locally
- [ ] All environment variables set in Vercel dashboard
- [ ] Database migrations applied to production
- [ ] CORS configured for API routes (if needed)
- [ ] Analytics/monitoring configured (Vercel Analytics or Sentry)
- [ ] Error boundaries in place for critical routes

---

**This CLAUDE.md is opinionated by design. Every rule exists to prevent common mistakes and enforce best practices for Next.js 15 + SQLite SaaS projects.**
