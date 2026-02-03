---
name: platxa-frontend-builder
description: Generate production-ready React/Next.js components for Platxa platform. Creates Server/Client components, forms, data tables, and UI primitives following App Router patterns, TypeScript best practices, and Tailwind/Shadcn styling.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
metadata:
  version: "1.0.0"
  tags:
    - builder
    - react
    - nextjs
    - frontend
    - typescript
---

# Platxa Frontend Builder

Generate production-ready React/Next.js components for the Platxa platform.

## Overview

This skill creates React components following Next.js 14+ App Router patterns, TypeScript best practices, and Platxa's design system. It integrates with `platxa-monaco-config` for editor components.

**What it creates:**
- Server Components (data fetching, layouts)
- Client Components (interactive UI, forms)
- Composite components (Card, Dialog, DataTable)
- Form components with Zod validation
- Accessible UI primitives

**Key features:**
- Automatic Server/Client component selection
- TypeScript with strict types and generics
- Tailwind CSS + Shadcn/ui styling
- React Hook Form + Zod validation
- ARIA accessibility patterns

## Workflow

### Step 1: Gather Requirements

Ask the user for:
- Component name and purpose
- Props/data it needs to display
- User interactions required
- Related existing components

### Step 2: Analyze Context

Use Glob/Read to understand:
- Existing component patterns in `src/components/`
- Design tokens in `tailwind.config.ts`
- Form schemas in `src/schemas/`
- State management patterns

### Step 3: Determine Component Type

| Requirement | Component Type | Directive |
|-------------|---------------|-----------|
| Data fetching | Server Component | None (default) |
| Event handlers | Client Component | `'use client'` |
| useState/useEffect | Client Component | `'use client'` |
| Browser APIs | Client Component | `'use client'` |
| Static content | Server Component | None |

### Step 4: Generate Component

Create the component following templates below, then:
1. Write component file to appropriate directory
2. Export from index if barrel exports used
3. Add TypeScript types/interfaces
4. Include JSDoc for complex props

### Step 5: Validate Output

Verify the component:
- TypeScript compiles without errors
- Props are properly typed
- Accessibility attributes present
- Follows project conventions

## Templates

### Server Component (Data Fetching)

```tsx
// app/[route]/page.tsx or components/[Name].tsx
import { db } from '@/lib/db';

interface PageProps {
  params: { id: string };
}

export default async function ResourcePage({ params }: PageProps) {
  const data = await db.resource.findUnique({ where: { id: params.id } });

  if (!data) {
    return <div>Not found</div>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{data.title}</h1>
      <p className="text-muted-foreground">{data.description}</p>
    </div>
  );
}
```

### Client Component (Interactive)

```tsx
'use client';

import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';

interface CounterProps {
  initialValue?: number;
  onChange?: (value: number) => void;
}

export function Counter({ initialValue = 0, onChange }: CounterProps) {
  const [count, setCount] = useState(initialValue);

  const handleIncrement = useCallback(() => {
    const newValue = count + 1;
    setCount(newValue);
    onChange?.(newValue);
  }, [count, onChange]);

  return (
    <div className="flex items-center gap-2">
      <span className="text-lg font-medium">{count}</span>
      <Button onClick={handleIncrement} size="sm">
        Increment
      </Button>
    </div>
  );
}
```

### Form Component (React Hook Form + Zod)

```tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

type FormData = z.infer<typeof formSchema>;

interface ContactFormProps {
  onSubmit: (data: FormData) => Promise<void>;
  defaultValues?: Partial<FormData>;
}

export function ContactForm({ onSubmit, defaultValues }: ContactFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input id="name" {...register('name')} aria-describedby="name-error" />
        {errors.name && (
          <p id="name-error" className="text-sm text-destructive">
            {errors.name.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" {...register('email')} aria-describedby="email-error" />
        {errors.email && (
          <p id="email-error" className="text-sm text-destructive">
            {errors.email.message}
          </p>
        )}
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </Button>
    </form>
  );
}
```

### Data Table Component

```tsx
'use client';

import { useState, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';

interface Column<T> {
  key: keyof T;
  header: string;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

interface DataTableProps<T extends { id: string | number }> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;
}

export function DataTable<T extends { id: string | number }>({
  data,
  columns,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map((col) => (
            <TableHead key={String(col.key)}>{col.header}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row) => (
          <TableRow
            key={row.id}
            onClick={() => onRowClick?.(row)}
            className={onRowClick ? 'cursor-pointer hover:bg-muted' : ''}
          >
            {columns.map((col) => (
              <TableCell key={String(col.key)}>
                {col.render ? col.render(row[col.key], row) : String(row[col.key])}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

### Composition Pattern (Server + Client)

```tsx
// ServerWrapper.tsx (Server Component - no directive)
import { db } from '@/lib/db';
import { ClientInteractive } from './ClientInteractive';

export async function ServerWrapper() {
  const data = await db.items.findMany();

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Items</h2>
      {/* Pass server data to client component */}
      <ClientInteractive initialItems={data} />
    </div>
  );
}

// ClientInteractive.tsx
'use client';

import { useState } from 'react';

interface Item {
  id: string;
  name: string;
}

interface ClientInteractiveProps {
  initialItems: Item[];
}

export function ClientInteractive({ initialItems }: ClientInteractiveProps) {
  const [items, setItems] = useState(initialItems);
  const [filter, setFilter] = useState('');

  const filtered = items.filter((item) =>
    item.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter items..."
        className="px-3 py-2 border rounded-md"
      />
      <ul className="mt-4 space-y-2">
        {filtered.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Examples

### Example 1: Create a User Profile Card

**User**: "Create a user profile card that shows avatar, name, and email"

**Response**:

```tsx
// components/UserProfileCard.tsx
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
}

interface UserProfileCardProps {
  user: User;
}

export function UserProfileCard({ user }: UserProfileCardProps) {
  const initials = user.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="flex flex-row items-center gap-4">
        <Avatar className="h-12 w-12">
          <AvatarImage src={user.avatarUrl} alt={user.name} />
          <AvatarFallback>{initials}</AvatarFallback>
        </Avatar>
        <div>
          <h3 className="font-semibold">{user.name}</h3>
          <p className="text-sm text-muted-foreground">{user.email}</p>
        </div>
      </CardHeader>
    </Card>
  );
}
```

### Example 2: Create a Settings Form

**User**: "Create a settings form for notification preferences"

**Response**:

```tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

const settingsSchema = z.object({
  emailNotifications: z.boolean(),
  pushNotifications: z.boolean(),
  weeklyDigest: z.boolean(),
});

type SettingsData = z.infer<typeof settingsSchema>;

interface NotificationSettingsProps {
  defaultValues: SettingsData;
  onSave: (data: SettingsData) => Promise<void>;
}

export function NotificationSettings({ defaultValues, onSave }: NotificationSettingsProps) {
  const { register, handleSubmit, watch, setValue, formState: { isSubmitting } } = useForm<SettingsData>({
    resolver: zodResolver(settingsSchema),
    defaultValues,
  });

  return (
    <form onSubmit={handleSubmit(onSave)} className="space-y-6">
      <div className="flex items-center justify-between">
        <Label htmlFor="email">Email notifications</Label>
        <Switch
          id="email"
          checked={watch('emailNotifications')}
          onCheckedChange={(checked) => setValue('emailNotifications', checked)}
        />
      </div>

      <div className="flex items-center justify-between">
        <Label htmlFor="push">Push notifications</Label>
        <Switch
          id="push"
          checked={watch('pushNotifications')}
          onCheckedChange={(checked) => setValue('pushNotifications', checked)}
        />
      </div>

      <div className="flex items-center justify-between">
        <Label htmlFor="digest">Weekly digest</Label>
        <Switch
          id="digest"
          checked={watch('weeklyDigest')}
          onCheckedChange={(checked) => setValue('weeklyDigest', checked)}
        />
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save Settings'}
      </Button>
    </form>
  );
}
```

## Output Checklist

When generating a component, verify:

- [ ] Correct directive (`'use client'` only when needed)
- [ ] Props interface defined with TypeScript
- [ ] Proper accessibility (labels, aria attributes)
- [ ] Consistent with project naming conventions
- [ ] Uses Shadcn/ui components where appropriate
- [ ] Tailwind classes follow design system
- [ ] Event handlers use `useCallback` when passed as props
- [ ] Forms have validation with Zod schema
- [ ] Error states handled and displayed
- [ ] Loading states for async operations

## Related Skills

- **platxa-monaco-config**: Monaco editor configuration for code editing components
- **platxa-testing**: Generate tests for React components using Vitest

## File Naming Conventions

| Component Type | File Pattern | Example |
|---------------|--------------|---------|
| Page | `page.tsx` | `app/dashboard/page.tsx` |
| Layout | `layout.tsx` | `app/dashboard/layout.tsx` |
| UI Component | `PascalCase.tsx` | `components/UserCard.tsx` |
| Hook | `use[Name].ts` | `hooks/useUser.ts` |
| Utility | `camelCase.ts` | `lib/formatDate.ts` |
| Schema | `[name].schema.ts` | `schemas/user.schema.ts` |
