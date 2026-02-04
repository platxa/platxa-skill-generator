# Hugging Face Path Format

DuckDB accesses Hub datasets through the `hf://` protocol, which resolves to auto-converted Parquet files.

## Path Structure

```
hf://datasets/{dataset_id}@{revision}/{config}/{split}/*.parquet
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| dataset_id | Owner/repo name | `cais/mmlu` |
| revision | Branch or special ref | `~parquet` (auto-converted) |
| config | Dataset subset/config | `default`, `ParaphraseRC` |
| split | Data split | `train`, `test`, `validation`, `*` |

### Examples

```
hf://datasets/cais/mmlu@~parquet/default/train/*.parquet
hf://datasets/ibm/duorc@~parquet/ParaphraseRC/test/*.parquet
hf://datasets/squad@~parquet/default/train/*.parquet
```

## The `@~parquet` Revision

The `~parquet` special revision provides auto-converted Parquet files for any dataset format (CSV, JSON, JSONL, etc.). This is the default used by `sql_manager.py` and is recommended for all queries.

## Wildcards

- `*` for split matches all splits: `hf://datasets/cais/mmlu@~parquet/default/*/*.parquet`
- Use `*` for config to match all configs: `hf://datasets/ibm/duorc@~parquet/*/*/*.parquet`

## Private Datasets

For private datasets, authentication is handled by setting the HF token in DuckDB:

```sql
CREATE SECRET hf_token (TYPE HUGGINGFACE, TOKEN 'hf_...');
```

The `sql_manager.py` script handles this automatically when `HF_TOKEN` is set.

## Multi-Dataset Joins

Reference multiple datasets using their full `hf://` paths:

```sql
SELECT a.*, b.*
FROM 'hf://datasets/dataset1@~parquet/default/train/*.parquet' a
JOIN 'hf://datasets/dataset2@~parquet/default/train/*.parquet' b
ON a.id = b.id
```

Use the `raw` command in `sql_manager.py` for these queries.
