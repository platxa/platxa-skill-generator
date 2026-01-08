# Domain Discovery Pattern

Framework for researching domain knowledge before skill creation.

## Discovery Framework

### Phase 1: Automatic Research

Performed without user interaction using Task tool subagents.

**Web Search Targets**:
1. Official documentation
2. Industry standards (ISO, W3C, OWASP, etc.)
3. Best practice guides
4. Tutorial sites
5. Stack Overflow discussions

**Existing Skill Analysis**:
1. Scan `~/.claude/skills/` for similar skills
2. Analyze `.claude/skills/` in current project
3. Extract patterns from successful skills

**Knowledge Classification**:
- **Domain Expertise (WHAT)**: Facts, concepts, terminology
- **Procedural Knowledge (HOW)**: Workflows, processes, steps

---

### Phase 2: Sufficiency Check

Evaluate if automatic research gathered enough information.

**Sufficiency Criteria**:
```
□ Core domain concepts identified (≥5)
□ Best practices documented (≥3)
□ Primary workflow understood
□ Key tools/technologies identified
□ Sources are authoritative
□ No critical gaps remain
```

**Decision Matrix**:

| Research Quality | Gaps Found | Action |
|------------------|------------|--------|
| High | None | Proceed to Architecture |
| High | Minor | Proceed with notes |
| Medium | Some | Ask user 1-2 questions |
| Low | Many | Ask user for guidance |

---

### Phase 3: User Clarification (If Needed)

Only ask questions when automatic research has gaps.

**Good Questions** (specific, actionable):
- "Should this skill support X or Y format?"
- "What's the typical file structure in your projects?"
- "Do you use framework A or B?"

**Bad Questions** (vague, unnecessary):
- "What should this skill do?" (already provided)
- "What are best practices?" (should research)
- "How does X work?" (should look up)

---

## Discovery Output Structure

```json
{
  "domain": {
    "name": "string",
    "description": "string",
    "related_domains": ["string"]
  },
  "knowledge": {
    "concepts": [
      {"term": "string", "definition": "string"}
    ],
    "best_practices": [
      {"practice": "string", "rationale": "string"}
    ],
    "anti_patterns": [
      {"pattern": "string", "why_avoid": "string"}
    ]
  },
  "workflow": {
    "steps": [
      {"order": 1, "action": "string", "details": "string"}
    ],
    "variations": ["string"],
    "decision_points": ["string"]
  },
  "tools": {
    "required": ["string"],
    "optional": ["string"],
    "claude_tools": ["Read", "Write", "etc"]
  },
  "sources": [
    {"title": "string", "url": "string", "authority": "high|medium|low"}
  ],
  "gaps": [
    {"topic": "string", "question": "string", "impact": "high|medium|low"}
  ],
  "sufficiency": {
    "score": 0.0-1.0,
    "ready": true|false,
    "blockers": ["string"]
  }
}
```

---

## Research Quality Indicators

### High Quality Sources
- Official documentation (framework, language, tool)
- Standards bodies (IETF, W3C, ISO)
- Peer-reviewed publications
- Major tech company engineering blogs

### Medium Quality Sources
- Popular tutorials (with dates)
- Stack Overflow answers (high votes)
- Community best practice guides
- Conference talks/presentations

### Low Quality Sources
- Outdated blog posts (>2 years)
- Forum posts with no verification
- AI-generated content
- Opinion pieces without evidence

---

## Variation Analysis

Identify what changes vs. what stays constant:

| Varies by Project | Constant |
|-------------------|----------|
| Directory structure | Core concepts |
| Naming conventions | Best practices |
| Framework choice | Quality criteria |
| Team preferences | Security requirements |

This analysis determines what the skill should ask users about vs. what it can assume.
