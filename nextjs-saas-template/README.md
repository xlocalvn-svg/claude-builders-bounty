# Next.js 15 + SQLite SaaS CLAUDE.md Template

An opinionated, production-ready `CLAUDE.md` template for greenfield SaaS projects using Next.js 15 App Router and SQLite.

## Setup

1. Copy the template into your project root:
   ```bash
   cp CLAUDE.md /path/to/your/nextjs-saas/CLAUDE.md
   ```

2. Start Claude Code in that project:
   ```bash
   cd /path/to/your/nextjs-saas && claude
   ```

3. Ask Claude Code to implement a feature. It should understand the stack, folder structure, DB rules, and anti-patterns without asking clarifying questions.

## What It Covers

- Stack and versions: Next.js 15, React 19, TypeScript 5, SQLite, Drizzle ORM, NextAuth v5, Tailwind 4
- Folder structure for App Router SaaS apps
- Naming conventions for routes, components, utilities, DB tables, and types
- SQL and migration conventions
- Server Component and Client Component patterns
- Server Actions and API route patterns
- Auth with NextAuth.js v5
- Dev commands
- Anti-patterns and the reason behind each one
- Performance, security, testing, and deployment checklists

## Why This Is Opinionated

Generic `CLAUDE.md` files cause Claude Code to ask too many clarification questions. This template makes clear decisions up front:

- App Router only, no Pages Router
- Server Components by default
- Drizzle ORM instead of Prisma
- SQLite via better-sqlite3 or Turso
- Tailwind for styling
- Strict TypeScript
- Named exports for components

Every rule includes a practical reason so Claude Code can follow the intent, not just the syntax.

## Testing Notes

This template was validated by simulating a greenfield Next.js 15 + SQLite SaaS project and checking that Claude Code had enough context to:

- Create route groups for auth and dashboard flows
- Use Server Components by default
- Place Drizzle schema and migrations in the correct folders
- Avoid raw SQL and `useEffect` data fetching
- Follow naming and migration conventions without additional clarification
