# DuckDB SQL Patterns for Hugging Face Datasets

Common SQL patterns when querying Hub datasets via `sql_manager.py`.

## Table Alias

Use `data` as the table name in queries. The tool replaces it with the actual `hf://` path:

```sql
SELECT * FROM data LIMIT 10
```

## String Functions

```sql
LENGTH(column)                     -- String length
LOWER(col), UPPER(col)            -- Case conversion
regexp_replace(col, '\n', '')      -- Regex replace
regexp_matches(col, 'pattern')     -- Regex match test
TRIM(col)                          -- Remove whitespace
CONCAT(col1, ' ', col2)           -- String concatenation
```

## Array Functions

```sql
choices[0]                         -- Array index (0-based)
array_length(choices)              -- Array length
unnest(choices)                    -- Expand array to rows
list_contains(tags, 'ml')         -- Check array membership
```

## Aggregations

```sql
SELECT col, COUNT(*) as cnt FROM data GROUP BY col ORDER BY cnt DESC
SELECT AVG(score), MIN(score), MAX(score) FROM data
SELECT col, COUNT(*) FROM data GROUP BY col HAVING COUNT(*) > 100
```

## Sampling

```sql
SELECT * FROM data USING SAMPLE 10                    -- Random sample
SELECT * FROM data USING SAMPLE 10 (RESERVOIR, 42)    -- Reproducible
SELECT * FROM data USING SAMPLE 5 PERCENT             -- Percentage-based
```

## Window Functions

```sql
SELECT *, ROW_NUMBER() OVER (PARTITION BY subject ORDER BY score DESC) as rank
FROM data
```

## DuckDB-Specific Features

```sql
-- Struct field access
SELECT metadata.language FROM data

-- List aggregation
SELECT subject, list(question ORDER BY question LIMIT 3) as sample_questions
FROM data GROUP BY subject

-- Pivot
PIVOT data ON subject USING COUNT(*)
```

## Common Query Patterns

### Quality Filtering

```sql
SELECT * FROM data
WHERE LENGTH(text) > 100
  AND LENGTH(text) < 10000
  AND text NOT LIKE '%TODO%'
```

### Deduplication

```sql
SELECT DISTINCT ON (question) * FROM data ORDER BY question, score DESC
```

### Format Conversion

```sql
SELECT question, choices[answer] as correct_answer, subject
FROM data
```
