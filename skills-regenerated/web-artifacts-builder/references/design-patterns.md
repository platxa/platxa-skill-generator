# Design Patterns for Web Artifacts

Component composition recipes and layout patterns for building polished artifacts.

## CSS Variable Theming

The shadcn/ui theme uses HSL CSS variables defined in `src/index.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  --primary: 0 0% 9%;
  --primary-foreground: 0 0% 98%;
  --secondary: 0 0% 96.1%;
  --muted: 0 0% 96.1%;
  --muted-foreground: 0 0% 45.1%;
  --accent: 0 0% 96.1%;
  --border: 0 0% 89.8%;
  --ring: 0 0% 3.9%;
  --radius: 0.5rem;
}
```

To customize, change the HSL values. Use `hsl(var(--primary))` in Tailwind classes via the extended theme config.

## Dashboard Layout Pattern

Grid-based layout with KPI row and content panels:

```tsx
function Dashboard() {
  return (
    <div className="min-h-screen bg-background p-6">
      <h1 className="text-2xl font-semibold tracking-tight mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard title="Revenue" value="$42,500" change="+12.5%" />
        <KpiCard title="Orders" value="1,234" change="+8.2%" />
        <KpiCard title="Customers" value="567" change="+3.1%" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card><CardContent className="pt-6"><Chart /></CardContent></Card>
        <Card><CardContent className="pt-6"><DataTable /></CardContent></Card>
      </div>
    </div>
  );
}
```

## KPI Card Pattern

Compact metric card with trend indicator:

```tsx
function KpiCard({ title, value, change }: {
  title: string; value: string; change: string;
}) {
  const isPositive = change.startsWith("+");
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className={cn("text-xs mt-1", isPositive ? "text-green-600" : "text-red-600")}>
          {change} from last period
        </p>
      </CardContent>
    </Card>
  );
}
```

## Form with Validation Pattern

Multi-field form using react-hook-form + zod:

```tsx
const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  role: z.enum(["admin", "user", "viewer"]),
});

function UserForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", email: "", role: "user" },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField control={form.control} name="name" render={({ field }) => (
          <FormItem>
            <FormLabel>Name</FormLabel>
            <FormControl><Input {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
```

## Data Table with Sorting Pattern

Sortable table with header click handlers:

```tsx
type SortDir = "asc" | "desc" | null;

function SortableTable({ data, columns }: Props) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);

  const sorted = useMemo(() => {
    if (!sortKey || !sortDir) return data;
    return [...data].sort((a, b) => {
      const cmp = String(a[sortKey]).localeCompare(String(b[sortKey]));
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  const toggleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(d => d === "asc" ? "desc" : d === "desc" ? null : "asc");
      if (sortDir === "desc") setSortKey(null);
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map(col => (
            <TableHead key={col.key} onClick={() => toggleSort(col.key)}
              className="cursor-pointer select-none">
              {col.label} {sortKey === col.key && (sortDir === "asc" ? "^" : "v")}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {sorted.map((row, i) => (
          <TableRow key={i}>
            {columns.map(col => <TableCell key={col.key}>{row[col.key]}</TableCell>)}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

## Dark Mode Toggle Pattern

Theme toggle using next-themes provider:

```tsx
import { ThemeProvider } from "next-themes";
import { Moon, Sun } from "lucide-react";

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system">
      <Layout />
    </ThemeProvider>
  );
}

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  return (
    <Button variant="outline" size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  );
}
```

## Anti-Slop Checklist

Before sharing any artifact, verify it avoids these patterns:

- [ ] No centered-everything layouts (use grid/flex with varied alignment)
- [ ] No purple or gradient backgrounds as primary design element
- [ ] No uniform `rounded-lg` on every element (vary radius by hierarchy)
- [ ] Color palette uses at most 2-3 colors plus neutrals
- [ ] Typography uses consistent scale (text-sm, text-base, text-lg, text-2xl)
- [ ] Spacing follows 4px grid (p-2, p-4, p-6, gap-4, gap-6)
- [ ] Interactive elements have visible hover/focus states
- [ ] Data is presented with real-looking values, not "Lorem ipsum"
