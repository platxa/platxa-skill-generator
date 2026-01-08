# Skill Creation State Schema

Schema for `.claude/skill_creation_state.json` - tracks workflow progress.

## Full Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SkillCreationState",
  "type": "object",
  "required": ["session_id", "phase", "created_at"],
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Unique identifier for this skill creation session"
    },
    "phase": {
      "type": "string",
      "enum": ["init", "discovery", "architecture", "generation", "validation", "installation", "complete"],
      "description": "Current workflow phase"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "When the session started"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp"
    },
    "input": {
      "type": "object",
      "properties": {
        "description": {
          "type": "string",
          "description": "User's skill description"
        },
        "target_users": {
          "type": "string",
          "description": "Who will use the skill"
        },
        "clarifications": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "question": { "type": "string" },
              "answer": { "type": "string" }
            }
          }
        }
      }
    },
    "discovery": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "complete", "failed"]
        },
        "sources_searched": {
          "type": "integer"
        },
        "findings": {
          "type": "object",
          "properties": {
            "domain": { "type": "string" },
            "key_concepts": { "type": "array", "items": { "type": "string" } },
            "best_practices": { "type": "array", "items": { "type": "string" } },
            "tools": { "type": "array", "items": { "type": "string" } }
          }
        },
        "sufficiency_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "gaps": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "architecture": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "complete", "failed"]
        },
        "skill_type": {
          "type": "string",
          "enum": ["Builder", "Guide", "Automation", "Analyzer", "Validator"]
        },
        "skill_name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9-]*$",
          "maxLength": 64
        },
        "directories": {
          "type": "array",
          "items": { "type": "string" }
        },
        "sections": {
          "type": "array",
          "items": { "type": "string" }
        },
        "scripts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "purpose": { "type": "string" }
            }
          }
        },
        "references": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "purpose": { "type": "string" }
            }
          }
        }
      }
    },
    "generation": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "complete", "failed"]
        },
        "output_directory": {
          "type": "string",
          "description": "Where generated files are written"
        },
        "artifacts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path": { "type": "string" },
              "type": { "type": "string", "enum": ["skill_md", "script", "reference", "asset"] },
              "size_bytes": { "type": "integer" },
              "created_at": { "type": "string", "format": "date-time" }
            }
          }
        }
      }
    },
    "validation": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "passed", "failed"]
        },
        "quality_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 10
        },
        "errors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "field": { "type": "string" },
              "message": { "type": "string" }
            }
          }
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "field": { "type": "string" },
              "message": { "type": "string" }
            }
          }
        },
        "checks": {
          "type": "object",
          "additionalProperties": { "type": "boolean" }
        }
      }
    },
    "installation": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "complete", "skipped"]
        },
        "location": {
          "type": "string",
          "enum": ["user", "project"]
        },
        "path": {
          "type": "string"
        },
        "installed_at": {
          "type": "string",
          "format": "date-time"
        }
      }
    },
    "progress": {
      "type": "object",
      "properties": {
        "phases_complete": {
          "type": "integer",
          "minimum": 0,
          "maximum": 6
        },
        "total_phases": {
          "type": "integer",
          "const": 6
        },
        "percent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        }
      }
    }
  }
}
```

## Example State File

```json
{
  "session_id": "skill_20260107_143022_a1b2c3",
  "phase": "validation",
  "created_at": "2026-01-07T14:30:22Z",
  "updated_at": "2026-01-07T14:45:18Z",
  "input": {
    "description": "A skill that generates API documentation from OpenAPI specs",
    "target_users": "Backend developers",
    "clarifications": []
  },
  "discovery": {
    "status": "complete",
    "sources_searched": 8,
    "findings": {
      "domain": "API Documentation",
      "key_concepts": ["OpenAPI 3.0", "Swagger", "REST conventions"],
      "best_practices": ["Include examples", "Document error responses"],
      "tools": ["Read", "Write", "WebFetch"]
    },
    "sufficiency_score": 0.85,
    "gaps": []
  },
  "architecture": {
    "status": "complete",
    "skill_type": "Builder",
    "skill_name": "api-doc-generator",
    "directories": ["scripts", "references"],
    "sections": ["Overview", "Workflow", "Examples", "Output Checklist"],
    "scripts": [
      {"name": "generate.sh", "purpose": "Generate docs from spec"}
    ],
    "references": [
      {"name": "openapi-guide.md", "purpose": "OpenAPI best practices"}
    ]
  },
  "generation": {
    "status": "complete",
    "output_directory": "/tmp/skill-gen/api-doc-generator",
    "artifacts": [
      {"path": "SKILL.md", "type": "skill_md", "size_bytes": 4200},
      {"path": "scripts/generate.sh", "type": "script", "size_bytes": 1500},
      {"path": "references/openapi-guide.md", "type": "reference", "size_bytes": 3000}
    ]
  },
  "validation": {
    "status": "passed",
    "quality_score": 8.5,
    "errors": [],
    "warnings": [
      {"field": "examples", "message": "Consider adding more examples"}
    ],
    "checks": {
      "skill_md_exists": true,
      "valid_frontmatter": true,
      "name_valid": true,
      "description_valid": true,
      "sections_present": true,
      "no_placeholders": true
    }
  },
  "installation": {
    "status": "pending",
    "location": null,
    "path": null
  },
  "progress": {
    "phases_complete": 4,
    "total_phases": 6,
    "percent": 66.7
  }
}
```

## Phase Transitions

```
init → discovery → architecture → generation → validation → installation → complete
                                                    ↓
                                              (if failed)
                                                    ↓
                                              generation (retry)
```

## Usage in Skill Generator

```markdown
1. On `/skill-generator` invocation:
   - Create new state file with phase="init"

2. After user input:
   - Update input section
   - Transition to phase="discovery"

3. After each phase completes:
   - Update relevant section
   - Update progress
   - Transition to next phase

4. On completion or abandonment:
   - Archive or delete state file
```
