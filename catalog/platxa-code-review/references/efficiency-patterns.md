# Efficiency Anti-Patterns

Common performance issues across languages with detection patterns and fixes.

## N+1 Queries

**Detection:** Loop body contains database query fetching a single item.

**Python (SQLAlchemy/Django):**
```python
# BAD: N+1
for order in orders:
    customer = db.query(Customer).get(order.customer_id)

# GOOD: Eager load
orders = db.query(Order).options(joinedload(Order.customer)).all()
```

**TypeScript (Prisma/TypeORM):**
```typescript
// BAD: N+1
for (const post of posts) {
  const author = await prisma.user.findUnique({ where: { id: post.authorId } })
}

// GOOD: Batch
const posts = await prisma.post.findMany({ include: { author: true } })
```

**Go (database/sql):**
```go
// BAD: N+1
for _, id := range userIDs {
    row := db.QueryRow("SELECT name FROM users WHERE id = $1", id)
}

// GOOD: Batch
rows, _ := db.Query("SELECT name FROM users WHERE id = ANY($1)", pq.Array(userIDs))
```

**Score impact:** -2.0 per occurrence

---

## String Concatenation in Loops

**Detection:** String variable reassigned with `+` or `+=` inside a loop.

```python
# BAD: O(n^2)
result = ""
for item in items:
    result += str(item) + ","

# GOOD: O(n)
result = ",".join(str(item) for item in items)
```

```java
// BAD: O(n^2)
String result = "";
for (String s : items) { result += s; }

// GOOD: O(n)
StringBuilder sb = new StringBuilder();
for (String s : items) { sb.append(s); }
```

**Score impact:** -1.0 per occurrence

---

## Unnecessary Object Creation in Loops

**Detection:** Object or collection instantiated inside loop when it could be outside.

```python
# BAD: Compiles regex every iteration
for line in lines:
    match = re.compile(r"\d+").search(line)

# GOOD: Compile once
pattern = re.compile(r"\d+")
for line in lines:
    match = pattern.search(line)
```

**Score impact:** -1.0 per occurrence

---

## Unbounded Collection Growth

**Detection:** Collection grows in loop or handler without size check or eviction.

```python
# BAD: Memory leak in long-running process
cache = {}
def handle_request(key, value):
    cache[key] = value  # Grows forever

# GOOD: Bounded cache
from functools import lru_cache
@lru_cache(maxsize=1000)
def get_value(key): ...
```

**Score impact:** -2.0 (critical in long-running services)

---

## Blocking I/O in Async Context

**Detection:** Synchronous file/network/DB call inside async function.

```python
# BAD: Blocks event loop
async def handle():
    data = open("file.txt").read()
    result = requests.get("https://...")

# GOOD
async def handle():
    async with aiofiles.open("file.txt") as f:
        data = await f.read()
    async with httpx.AsyncClient() as client:
        result = await client.get("https://...")
```

**Score impact:** -2.0 per occurrence

---

## Fetch-All-Then-Filter

**Detection:** Query fetches all records, then filters in application code.

```python
# BAD: Fetches entire table
all_users = User.objects.all()
active = [u for u in all_users if u.is_active]

# GOOD: Filter at database
active = User.objects.filter(is_active=True)
```

**Score impact:** -1.5 per occurrence

---

## Redundant Computation

**Detection:** Same expensive calculation performed multiple times.

```python
# BAD: Computes len() twice per iteration
for i in range(len(items)):
    if i < len(items) - 1:
        ...

# GOOD
count = len(items)
for i in range(count):
    if i < count - 1:
        ...
```

**Score impact:** -0.5 per occurrence

---

## Missing Early Return

**Detection:** Entire function body wrapped in condition, or deep nesting.

```python
# BAD: Deep nesting
def process(items):
    if items:
        if len(items) > 0:
            for item in items:
                if item.is_valid():
                    ...  # 4 levels deep

# GOOD: Guard clauses
def process(items):
    if not items:
        return
    for item in items:
        if not item.is_valid():
            continue
        ...  # 2 levels
```

**Score impact:** -0.5 per occurrence

---

## Summary: Detection Priority

| Anti-Pattern | Impact | Frequency | Detection Difficulty |
|-------------|--------|-----------|---------------------|
| N+1 queries | Very High | Common | Medium |
| Unbounded growth | Very High | Common | Medium |
| Blocking I/O | High | Common | Easy |
| String concat in loops | Medium | Very Common | Easy |
| Object creation in loops | Medium | Common | Easy |
| Fetch-all-then-filter | Medium | Common | Medium |
| Redundant computation | Low-Medium | Very Common | Medium |
| Missing early return | Low | Very Common | Easy |
