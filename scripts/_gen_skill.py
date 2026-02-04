#!/usr/bin/env python3
"""Temporary helper to run score_skill on a directory."""

import json
import sys
from pathlib import Path

# Import the scoring module
sys.path.insert(0, str(Path(__file__).parent))
from importlib.util import module_from_spec, spec_from_file_location

_spec = spec_from_file_location("score_mod", Path(__file__).parent / "score-skill.py")
assert _spec is not None and _spec.loader is not None
mod = module_from_spec(_spec)
_spec.loader.exec_module(mod)

skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("skills-regenerated/netlify-deploy")
report = mod.score_skill(skill_dir)
print(json.dumps(report, indent=2))
sys.exit(0 if report["passed"] else 1)
