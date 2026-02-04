# Regeneration Pipeline

Transform an upstream skill into a Platxa-native skill by extracting its intent, enriching with research, and regenerating through the standard skill creation pipeline.

## When to Use

Use this workflow when an upstream skill exists but doesn't meet Platxa standards. Instead of copying and patching, extract the intent and regenerate from scratch.

## Input Modes

Two mutually exclusive input modes:

### Mode A: Upstream Directory (full pipeline)
- **upstream_dir**: Path to the upstream skill directory (must contain SKILL.md)
- Starts from Phase 1 (Intent Extraction) through all phases

### Mode B: Pre-extracted Intent (skip Phase 1)
- **intent_file**: Path to a JSON file containing previously extracted intent
- Starts from Phase 2 (Discovery Enrichment) — Phase 1 is already done
- The intent file must contain DiscoveryFindings-compatible JSON with at minimum: skill_name, skill_type, description, domain, gaps

### Common Options
- **output_dir**: Where to write the regenerated skill (defaults to skills/{skill_name}/)

## Pipeline Phases

### Phase 1: Intent Extraction (skipped when intent_file provided)

Use Task tool with `subagent_type="general-purpose"` and the Intent Agent prompt from `references/agents/intent-agent.md`.

**Input**: The upstream skill directory path.

**What the agent does**:
1. Reads SKILL.md (frontmatter + body)
2. Reads all files in references/, scripts/, agents/, assets/, templates/
3. Understands the skill's purpose, domain, workflows, and tool needs semantically
4. Classifies skill type (Builder/Guide/Automation/Analyzer/Validator)
5. Assesses content richness (confidence score 0.0-1.0)
6. Identifies gaps where upstream content is thin

**Output**: DiscoveryFindings-compatible JSON with `gaps` field.

**Checkpoint**: Verify the extracted intent makes sense. If confidence < 0.3, the upstream content may be too thin to regenerate — flag for manual review.

### Phase 2: Discovery Enrichment

Use Task tool with `subagent_type="Explore"` and the Discovery Agent prompt from `references/agents/discovery-agent.md`.

**Input**: The gaps identified by the Intent Agent, plus the skill's domain and description.

**What the agent does**:
1. Takes the `gaps` list from Phase 1 as targeted research topics
2. Searches the web for best practices, documentation, and standards
3. Fills knowledge gaps with authoritative sources
4. Merges enriched findings with the Intent Agent's output

**Output**: Enriched DiscoveryFindings JSON with gaps filled.

**Skip condition**: If the Intent Agent's confidence >= 0.8 and gaps list is empty, skip this phase — the upstream content is rich enough.

### Phase 3: Architecture Design

Use Task tool with `subagent_type="general-purpose"` and the Architecture Agent prompt from `references/agents/architecture-agent.md`.

**Input**: The enriched DiscoveryFindings JSON from Phase 2.

**What the agent does**:
1. Determines the optimal Platxa skill type
2. Designs the directory structure (scripts/, references/)
3. Plans SKILL.md sections based on type templates
4. Allocates token budget
5. Selects allowed tools

**Output**: Architecture blueprint JSON.

This is the same Architecture phase used for new skill creation — the regeneration pipeline converges with the standard pipeline here.

### Phase 4: Content Generation

Use Task tool with `subagent_type="general-purpose"` and the Generation Agent prompt from `references/agents/generation-agent.md`.

**Input**: Architecture blueprint + enriched discovery findings.

**What the agent does**:
1. Creates SKILL.md with valid YAML frontmatter following the type template
2. Creates scripts/ with executable helpers (if architecture requires)
3. Creates references/ with domain documentation (if architecture requires)
4. Adds provenance metadata to frontmatter. All five fields are **required**:
   ```yaml
   metadata:
     provenance:
       upstream_source: "{skill-name}"
       upstream_sha: "{git SHA of upstream content, from: git log -1 --format=%H -- skills/{skill-name}/}"
       regenerated_at: "{ISO 8601 timestamp with timezone}"
       generator_version: "1.0.0"
       intent_confidence: {0.0-1.0 score from Intent Agent}
   ```

   To obtain `upstream_sha`, run:
   ```bash
   git log -1 --format=%H -- {upstream_dir}
   ```
   If the upstream skill is not tracked by git (untracked files), use `"untracked"` as the SHA value.

**Output**: Complete Platxa-native skill directory with provenance metadata in frontmatter.

### Phase 5: Validation

Run the standard validation suite:

```bash
./scripts/validate-all.sh {output_dir}
python3 scripts/score-skill.py {output_dir} --threshold 7.0
```

**Quality gate**: Score must be >= 7.0/10. If validation fails, loop back to Phase 4 with specific feedback.

### Phase 6: Installation

Write the regenerated skill to the output directory. If overwriting the upstream skill, ensure:
1. The upstream content is preserved (git tracks the diff)
2. Provenance metadata links back to the upstream source

## Dry-Run Mode

When running in dry-run mode, do NOT invoke any agents or generate any files. Instead, read the upstream content directly and produce a comprehensive regeneration plan.

### Steps

1. Read SKILL.md frontmatter (name, description, allowed-tools, metadata)
2. Read SKILL.md body (count lines, headers, code blocks)
3. Inventory all subdirectories and files
4. Read reference files (extract topic names from first header)
5. Read script files (extract purpose from docstring/comment)
6. Analyze the content to determine:
   - **Skill type**: Based on what the skill DOES (read the description and workflow)
   - **Planned sections**: Match to the type template in `references/templates/{type}-template.md`
   - **Token estimates**: Count words in SKILL.md (~0.75 tokens/word), estimate reference and script token needs
   - **Provenance metadata**: What will be recorded (upstream source, timestamp, generator version)

### Output Format

```
Regeneration Plan: {skill-name}
═══════════════════════════════════════════════════

Source: {upstream_dir}
Structure:
  - SKILL.md ({line_count} lines, ~{token_estimate} tokens)
  - references/ ({count} files)
  - scripts/ ({count} files)

Intent Summary:
  Name:         {name}
  Description:  {description (first 120 chars)}
  Skill Type:   {guide|builder|automation|analyzer|validator} — {reasoning}
  Domain:       {primary domain}

Architecture Blueprint:
  Type Template:   references/templates/{type}-template.md
  Planned Sections:
    - Overview
    - {Section 2 from template}
    - {Section 3 from template}
    - ...
  Directories:     {list of dirs to create: scripts/, references/, etc.}
  Allowed Tools:   {tools from frontmatter or inferred from content}
  Scripts:         {planned scripts with purposes, or "none"}
  References:      {planned reference files with topics, or "none"}

Token Estimates:
  SKILL.md:        ~{n} tokens (budget: 5000)
  References:      ~{n} tokens (budget: 10000)
  Total:           ~{n} tokens (budget: 15000)

Provenance:
  upstream_source:    {skill-name}
  upstream_sha:       {git SHA or "untracked"}
  regenerated_at:     {current ISO 8601 timestamp}
  generator_version:  1.0.0
  intent_confidence:  {0.0-1.0}

Pipeline:
  1. Intent Extraction    → intent-agent reads {upstream_dir}
  2. Discovery Enrichment → discovery-agent fills gaps
  3. Architecture Design  → architecture-agent designs Platxa structure
  4. Content Generation   → generation-agent creates skill
  5. Quality Validation   → validate-all.sh + score-skill.py >= 7.0

Output: {output_dir}
```

### Dry-Run with Intent File

When `--intent-file` is provided, read the JSON and show the intent summary from the file instead of analyzing the upstream directory. Include all fields from the intent JSON in the output.

## Batch Mode

For regenerating multiple skills, iterate over each skill directory:

```bash
for skill_dir in skills/*/; do
  # Skip non-upstream skills (check manifest for source)
  ./scripts/regenerate-skill.sh "$skill_dir" --dry-run
done
```

## Error Handling

- **Missing SKILL.md**: Skip with error message, log to regeneration report
- **Intent confidence < 0.3**: Flag for manual review, do not auto-regenerate
- **Validation score < 7.0**: Retry generation once with validation feedback, then flag if still failing
- **Agent timeout**: Log failure, continue with next skill in batch mode
