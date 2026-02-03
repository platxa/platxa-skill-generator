# TypeScript Patterns for React

## Component Props Typing

### Basic Props Interface

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}

export function Button({ label, onClick, disabled = false, variant = 'primary' }: ButtonProps) {
  return <button onClick={onClick} disabled={disabled}>{label}</button>;
}
```

### Extending HTML Elements

```typescript
import { ComponentPropsWithoutRef, forwardRef } from 'react';

interface InputProps extends ComponentPropsWithoutRef<'input'> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => (
    <div>
      <label>{label}</label>
      <input ref={ref} className={className} {...props} />
      {error && <span className="text-red-500">{error}</span>}
    </div>
  )
);
Input.displayName = 'Input';
```

### Children Props

```typescript
// ReactNode for any renderable content
interface CardProps {
  children: React.ReactNode;
  title?: string;
}

// ReactElement for specific element type
interface WrapperProps {
  children: React.ReactElement;
}

// Function as children (render props)
interface DataProviderProps<T> {
  children: (data: T) => React.ReactNode;
}
```

## Generic Components

### Generic List

```typescript
interface ListProps<T extends { id: string | number }> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor?: (item: T) => string | number;
}

export function List<T extends { id: string | number }>({
  items,
  renderItem,
  keyExtractor = (item) => item.id,
}: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Usage
<List<User>
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
/>
```

### Generic Form Field

```typescript
import { FieldPath, FieldValues, UseFormRegister } from 'react-hook-form';

interface FormFieldProps<T extends FieldValues> {
  name: FieldPath<T>;
  register: UseFormRegister<T>;
  label: string;
  type?: 'text' | 'email' | 'password';
}

export function FormField<T extends FieldValues>({
  name,
  register,
  label,
  type = 'text',
}: FormFieldProps<T>) {
  return (
    <div>
      <label htmlFor={name}>{label}</label>
      <input id={name} type={type} {...register(name)} />
    </div>
  );
}
```

## Discriminated Unions for State

```typescript
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function useAsync<T>() {
  const [state, setState] = useState<AsyncState<T>>({ status: 'idle' });

  const execute = async (promise: Promise<T>) => {
    setState({ status: 'loading' });
    try {
      const data = await promise;
      setState({ status: 'success', data });
    } catch (error) {
      setState({ status: 'error', error: error as Error });
    }
  };

  return { state, execute };
}

// Usage with exhaustive checking
function StatusDisplay<T>({ state }: { state: AsyncState<T> }) {
  switch (state.status) {
    case 'idle':
      return <div>Ready</div>;
    case 'loading':
      return <div>Loading...</div>;
    case 'success':
      return <div>Data loaded</div>;
    case 'error':
      return <div>Error: {state.error.message}</div>;
  }
}
```

## Type-Safe Event Handlers

```typescript
// Form events
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
};

// Input events
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

// Keyboard events
const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') submit();
};

// Mouse events
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.stopPropagation();
};
```

## Utility Types

```typescript
// Make all props optional
type PartialProps = Partial<UserProps>;

// Make specific props required
type RequiredProps = Required<Pick<UserProps, 'id'>> & Omit<UserProps, 'id'>;

// Exclude props
type WithoutId = Omit<User, 'id'>;

// Extract prop types from component
type ButtonPropsFromComponent = React.ComponentProps<typeof Button>;

// Extract return type
type UserData = Awaited<ReturnType<typeof fetchUser>>;
```

## Context with TypeScript

```typescript
interface AuthContextValue {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await authApi.login(credentials);
    setUser(user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

## Zod Schema Integration

```typescript
import { z } from 'zod';

const userSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  age: z.number().min(0).max(150).optional(),
});

// Infer TypeScript type from Zod schema
type User = z.infer<typeof userSchema>;

// Use in component props
interface UserFormProps {
  defaultValues?: Partial<User>;
  onSubmit: (data: User) => Promise<void>;
}
```
