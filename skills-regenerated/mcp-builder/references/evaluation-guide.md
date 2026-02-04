# MCP Server Evaluation Guide

## Purpose

Evaluations measure how effectively an LLM with no prior context can use your MCP server to answer realistic, complex questions. They test the quality of tool descriptions, schemas, and responses -- not just whether endpoints work.

## Question Requirements

Write 10 questions. Each must be:

- **Independent**: no dependency on other questions
- **Read-only**: only non-destructive, idempotent operations
- **Complex**: requires multiple tool calls (potentially dozens)
- **Realistic**: reflects tasks humans would actually perform
- **Verifiable**: single clear answer checkable by string comparison
- **Stable**: answer does not change over time (use historical/closed data)

## Question Design

**Multi-hop**: require sequential tool calls where each step uses information from the previous one.

**No keyword search shortcuts**: use synonyms and paraphrases so the LLM must reason about which tools to call.

**Stress-test responses**: require understanding IDs, timestamps, file names, URLs, and large JSON payloads.

**Specify output format** in the question when the answer could be ambiguous: "Use YYYY/MM/DD", "Answer True or False", "Provide the username".

**Answers must be single values**: a name, ID, number, date, boolean, or short string. Never a list or complex structure.

## Output Format

```xml
<evaluation>
  <qa_pair>
    <question>Find the repository archived in Q3 2023 that previously had the
    most forks in the organisation. What was its primary language?</question>
    <answer>Python</answer>
  </qa_pair>
  <qa_pair>
    <question>Among bugs reported in January 2024 marked critical, which
    assignee resolved the highest percentage within 48 hours? Provide
    their username.</question>
    <answer>alex_eng</answer>
  </qa_pair>
</evaluation>
```

## Evaluation Process

1. **Inspect documentation**: read the target API docs to understand endpoints
2. **Inspect tools**: list MCP server tools, read schemas and descriptions
3. **Explore content**: use read-only tools to identify specific data for questions (use `limit` < 10, paginate)
4. **Write questions**: create 10 questions following all guidelines
5. **Verify answers**: solve each question yourself using the tools
6. **Remove invalid pairs**: drop any that require write operations or have unstable answers

## Running the Harness

Install dependencies:

```bash
pip install anthropic mcp
export ANTHROPIC_API_KEY=your_key
```

Run against a stdio server:

```bash
python scripts/evaluation.py \
  -t stdio \
  -c python -a my_server.py \
  -e API_KEY=abc123 \
  evaluation.xml
```

Run against a streamable HTTP server (start server first):

```bash
python scripts/evaluation.py \
  -t http \
  -u http://localhost:3000/mcp \
  -H "Authorization: Bearer token" \
  evaluation.xml
```

Save report:

```bash
python scripts/evaluation.py \
  -t stdio -c node -a dist/index.js \
  -o report.md \
  evaluation.xml
```

## Report Contents

- Accuracy: correct/total
- Average duration and tool calls per question
- Per-question: expected vs actual answer, pass/fail, agent feedback
- Tool call details for debugging

## Improving Low Scores

- Review agent feedback for each failed question
- Check if tool descriptions are clear and complete
- Verify input parameter documentation
- Ensure tools return focused data (not overwhelming JSON)
- Confirm error messages guide the LLM toward correct usage
- Add `limit` parameters to prevent context overflow
