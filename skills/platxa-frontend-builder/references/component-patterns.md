# React Component Patterns Reference

## Server vs Client Components

### When to Use Server Components (Default)

- Data fetching from database or API
- Accessing backend resources directly
- Keeping sensitive data on server (API keys, tokens)
- Large dependencies that shouldn't ship to client
- Static content rendering

```tsx
// No directive needed - Server Component by default
import { db } from '@/lib/db';

export default async function ProductList() {
  const products = await db.product.findMany();
  return (
    <ul>
      {products.map((p) => <li key={p.id}>{p.name}</li>)}
    </ul>
  );
}
```

### When to Use Client Components

- Event listeners (onClick, onChange)
- State (useState, useReducer)
- Effects (useEffect, useLayoutEffect)
- Browser APIs (localStorage, geolocation)
- Custom hooks with state/effects
- React Context consumers

```tsx
'use client';

import { useState } from 'react';

export function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('');

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      onKeyDown={(e) => e.key === 'Enter' && onSearch(query)}
    />
  );
}
```

## Composition Patterns

### Server Parent with Client Child

```tsx
// ServerPage.tsx (Server Component)
import { db } from '@/lib/db';
import { InteractiveList } from './InteractiveList';

export default async function ServerPage() {
  const items = await db.items.findMany();
  return <InteractiveList items={items} />;
}

// InteractiveList.tsx (Client Component)
'use client';

export function InteractiveList({ items }: { items: Item[] }) {
  const [selected, setSelected] = useState<string | null>(null);
  return (
    <ul>
      {items.map((item) => (
        <li
          key={item.id}
          onClick={() => setSelected(item.id)}
          className={selected === item.id ? 'bg-blue-100' : ''}
        >
          {item.name}
        </li>
      ))}
    </ul>
  );
}
```

### Children as Server Components

```tsx
// ClientModal.tsx
'use client';

export function Modal({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return open ? <div className="modal">{children}</div> : null;
}

// Page.tsx (Server Component)
import { Modal } from './ClientModal';
import { ServerContent } from './ServerContent';

export default function Page() {
  return (
    <Modal>
      <ServerContent /> {/* Server Component as child */}
    </Modal>
  );
}
```

## Loading and Error States

### Suspense Boundaries

```tsx
import { Suspense } from 'react';

function LoadingSkeleton() {
  return <div className="animate-pulse bg-gray-200 h-32 rounded" />;
}

export default function Dashboard() {
  return (
    <div className="grid gap-4">
      <Suspense fallback={<LoadingSkeleton />}>
        <AsyncMetrics />
      </Suspense>
      <Suspense fallback={<LoadingSkeleton />}>
        <AsyncChart />
      </Suspense>
    </div>
  );
}
```

### Error Boundaries

```tsx
// error.tsx (must be Client Component)
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="p-4 bg-red-50 rounded">
      <h2 className="text-red-800">Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

## Data Fetching Patterns

### Server Actions

```tsx
// actions/user.ts
'use server';

import { db } from '@/lib/db';

export async function updateUser(formData: FormData) {
  const name = formData.get('name') as string;
  await db.user.update({ where: { id: userId }, data: { name } });
}

// Form.tsx
'use client';

import { updateUser } from '@/actions/user';

export function UpdateForm() {
  return (
    <form action={updateUser}>
      <input name="name" />
      <button type="submit">Update</button>
    </form>
  );
}
```

### React Query Integration

```tsx
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function UserList() {
  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then((r) => r.json()),
  });

  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (id: string) => fetch(`/api/users/${id}`, { method: 'DELETE' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });

  if (isLoading) return <div>Loading...</div>;
  return (
    <ul>
      {data.map((user) => (
        <li key={user.id}>
          {user.name}
          <button onClick={() => mutation.mutate(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

## Optimization Patterns

### Memoization

```tsx
import { memo, useCallback, useMemo } from 'react';

const ExpensiveItem = memo(({ item, onSelect }: ItemProps) => {
  return <div onClick={() => onSelect(item.id)}>{item.name}</div>;
});

export function List({ items, onSelect }: ListProps) {
  const handleSelect = useCallback((id: string) => {
    onSelect(id);
  }, [onSelect]);

  const sortedItems = useMemo(() =>
    [...items].sort((a, b) => a.name.localeCompare(b.name)),
    [items]
  );

  return sortedItems.map((item) => (
    <ExpensiveItem key={item.id} item={item} onSelect={handleSelect} />
  ));
}
```
