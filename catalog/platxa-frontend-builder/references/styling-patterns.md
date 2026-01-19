# Styling Patterns Reference

## Tailwind CSS Patterns

### Responsive Design (Mobile-First)

```tsx
// Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
<div className="
  grid grid-cols-1 gap-4
  sm:grid-cols-2
  lg:grid-cols-3
  xl:grid-cols-4
">
  {items.map(item => <Card key={item.id} />)}
</div>

// Responsive text
<h1 className="text-xl sm:text-2xl lg:text-4xl font-bold">
  Responsive Heading
</h1>
```

### Dark Mode

```tsx
// Use dark: prefix for dark mode styles
<div className="bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
  <p className="text-gray-600 dark:text-gray-400">Description</p>
</div>

// Cards with dark mode
<div className="
  bg-white border border-gray-200 shadow-sm
  dark:bg-gray-800 dark:border-gray-700
  rounded-lg p-4
">
  Content
</div>
```

### Interactive States

```tsx
// Hover, focus, active states
<button className="
  bg-blue-600 text-white px-4 py-2 rounded-md
  hover:bg-blue-700
  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  active:bg-blue-800
  disabled:bg-gray-400 disabled:cursor-not-allowed
  transition-colors
">
  Click Me
</button>

// Group hover
<div className="group p-4 hover:bg-gray-100 rounded-lg">
  <h3 className="font-medium group-hover:text-blue-600">Title</h3>
  <p className="text-gray-600 group-hover:text-gray-900">Description</p>
</div>
```

### Common Layout Patterns

```tsx
// Centered content
<div className="flex items-center justify-center min-h-screen">
  <div className="max-w-md w-full p-6">Content</div>
</div>

// Sticky header
<header className="sticky top-0 z-50 bg-white/80 backdrop-blur-sm border-b">
  <nav className="container mx-auto px-4 h-16 flex items-center">
    Navigation
  </nav>
</header>

// Sidebar layout
<div className="flex">
  <aside className="w-64 shrink-0 border-r h-screen sticky top-0">
    Sidebar
  </aside>
  <main className="flex-1 p-6">Content</main>
</div>
```

## Shadcn/ui Patterns

### Using cn() Utility

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage in components
interface CardProps {
  className?: string;
  variant?: 'default' | 'outline';
}

export function Card({ className, variant = 'default' }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg p-4',
        variant === 'default' && 'bg-white shadow-md',
        variant === 'outline' && 'border border-gray-200',
        className
      )}
    />
  );
}
```

### Class Variance Authority (CVA)

```typescript
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size, className }))} {...props} />
  );
}
```

### Composable Components

```tsx
// Card components
export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('rounded-lg border bg-card shadow-sm', className)} {...props} />;
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn('text-2xl font-semibold', className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-6 pt-0', className)} {...props} />;
}

// Usage
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>
```

## Design Tokens

```css
/* globals.css - CSS custom properties */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark mode values */
  }
}
```

## Accessibility Styling

```tsx
// Focus visible for keyboard navigation
<button className="
  focus:outline-none
  focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
">
  Keyboard Accessible
</button>

// Screen reader only text
<span className="sr-only">Close menu</span>

// Skip link
<a href="#main-content" className="
  sr-only focus:not-sr-only
  focus:absolute focus:top-4 focus:left-4
  focus:z-50 focus:bg-white focus:p-4 focus:rounded
">
  Skip to main content
</a>
```
