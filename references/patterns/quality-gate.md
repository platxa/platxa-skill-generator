# Quality Gate

Enforce minimum quality thresholds before skill installation.

## Purpose

The quality gate is the final checkpoint that blocks low-quality skills from being installed. It enforces hard thresholds that cannot be bypassed.

## Gate Thresholds

| Gate | Threshold | Type | Bypass |
|------|-----------|------|--------|
| Overall Score | ≥ 7.0 | Hard | No |
| Spec Compliance | 100% | Hard | No |
| Content Quality | ≥ 6.0 | Soft | With warning |
| Expertise Depth | ≥ 6.0 | Soft | With warning |
| Token Budget | Pass | Hard | No |
| Script Tests | Pass | Hard | No |

## Gate Implementation

```python
from dataclasses import dataclass
from enum import Enum

class GateResult(Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"

@dataclass
class QualityGateResult:
    passed: bool
    result: GateResult
    score: float
    gates_checked: int
    gates_passed: int
    gates_warned: int
    gates_failed: int
    details: dict
    message: str

# Threshold configuration
THRESHOLDS = {
    'overall_score': {'value': 7.0, 'type': 'hard'},
    'spec_compliance': {'value': 1.0, 'type': 'hard'},  # 100%
    'content_quality': {'value': 6.0, 'type': 'soft'},
    'expertise_depth': {'value': 6.0, 'type': 'soft'},
    'token_budget': {'value': True, 'type': 'hard'},    # Boolean pass
    'script_tests': {'value': True, 'type': 'hard'},    # Boolean pass
}


def check_quality_gate(quality_assessment: dict) -> QualityGateResult:
    """
    Check if skill passes quality gate.

    Args:
        quality_assessment: Output from quality aggregator

    Returns:
        QualityGateResult with pass/fail decision
    """
    gates_passed = 0
    gates_warned = 0
    gates_failed = 0
    details = {}

    overall_score = quality_assessment.get('overall_score', 0)
    components = quality_assessment.get('components', {})

    # 1. Overall score gate (HARD)
    gate_result = check_threshold(
        overall_score,
        THRESHOLDS['overall_score']['value'],
        'hard'
    )
    details['overall_score'] = {
        'value': overall_score,
        'threshold': 7.0,
        'result': gate_result.value
    }
    if gate_result == GateResult.PASS:
        gates_passed += 1
    elif gate_result == GateResult.WARN:
        gates_warned += 1
    else:
        gates_failed += 1

    # 2. Spec compliance gate (HARD)
    spec_score = components.get('spec_compliance', {}).get('score', 0) / 10
    gate_result = check_threshold(spec_score, 1.0, 'hard')
    details['spec_compliance'] = {
        'value': spec_score,
        'threshold': 1.0,
        'result': gate_result.value
    }
    if gate_result == GateResult.PASS:
        gates_passed += 1
    else:
        gates_failed += 1

    # 3. Content quality gate (SOFT)
    content_score = components.get('content_quality', {}).get('score', 0)
    gate_result = check_threshold(content_score, 6.0, 'soft')
    details['content_quality'] = {
        'value': content_score,
        'threshold': 6.0,
        'result': gate_result.value
    }
    if gate_result == GateResult.PASS:
        gates_passed += 1
    elif gate_result == GateResult.WARN:
        gates_warned += 1
    else:
        gates_failed += 1

    # 4. Expertise depth gate (SOFT)
    expertise_score = components.get('expertise_depth', {}).get('score', 0)
    gate_result = check_threshold(expertise_score, 6.0, 'soft')
    details['expertise_depth'] = {
        'value': expertise_score,
        'threshold': 6.0,
        'result': gate_result.value
    }
    if gate_result == GateResult.PASS:
        gates_passed += 1
    elif gate_result == GateResult.WARN:
        gates_warned += 1
    else:
        gates_failed += 1

    # 5. Token budget gate (HARD)
    token_passed = components.get('token_budget', {}).get('passed', False)
    gate_result = GateResult.PASS if token_passed else GateResult.FAIL
    details['token_budget'] = {
        'value': token_passed,
        'threshold': True,
        'result': gate_result.value
    }
    if gate_result == GateResult.PASS:
        gates_passed += 1
    else:
        gates_failed += 1

    # 6. Script tests gate (HARD, if applicable)
    if 'scripts' in components:
        scripts_passed = components.get('scripts', {}).get('passed', False)
        gate_result = GateResult.PASS if scripts_passed else GateResult.FAIL
        details['script_tests'] = {
            'value': scripts_passed,
            'threshold': True,
            'result': gate_result.value
        }
        if gate_result == GateResult.PASS:
            gates_passed += 1
        else:
            gates_failed += 1

    # Determine overall gate result
    gates_checked = gates_passed + gates_warned + gates_failed

    if gates_failed > 0:
        passed = False
        result = GateResult.FAIL
        message = generate_failure_message(details)
    elif gates_warned > 0:
        passed = True
        result = GateResult.WARN
        message = generate_warning_message(details)
    else:
        passed = True
        result = GateResult.PASS
        message = f"Quality gate PASSED. Score: {overall_score:.1f}/10"

    return QualityGateResult(
        passed=passed,
        result=result,
        score=overall_score,
        gates_checked=gates_checked,
        gates_passed=gates_passed,
        gates_warned=gates_warned,
        gates_failed=gates_failed,
        details=details,
        message=message
    )


def check_threshold(value: float, threshold: float, gate_type: str) -> GateResult:
    """Check a single threshold."""
    if isinstance(threshold, bool):
        return GateResult.PASS if value == threshold else GateResult.FAIL

    if value >= threshold:
        return GateResult.PASS
    elif gate_type == 'soft' and value >= threshold * 0.8:
        return GateResult.WARN
    else:
        return GateResult.FAIL
```

## Message Generation

```python
def generate_failure_message(details: dict) -> str:
    """Generate descriptive failure message."""
    failed_gates = [
        name for name, info in details.items()
        if info['result'] == 'fail'
    ]

    if 'overall_score' in failed_gates:
        score = details['overall_score']['value']
        return (
            f"Quality gate FAILED. Score {score:.1f}/10 is below "
            f"minimum threshold of 7.0. Skill cannot be installed."
        )

    if 'spec_compliance' in failed_gates:
        return (
            "Quality gate FAILED. Skill does not comply with "
            "Agent Skills Spec v1.0. Fix compliance issues first."
        )

    return f"Quality gate FAILED. Issues: {', '.join(failed_gates)}"


def generate_warning_message(details: dict) -> str:
    """Generate warning message for soft failures."""
    warned_gates = [
        name for name, info in details.items()
        if info['result'] == 'warn'
    ]

    return (
        f"Quality gate PASSED with warnings. "
        f"Consider improving: {', '.join(warned_gates)}"
    )
```

## Gate Visualization

```
Quality Gate Check
══════════════════════════════════════════════════════

  Overall Score:     8.2 / 7.0   ✓ PASS
  Spec Compliance:   100%        ✓ PASS
  Content Quality:   7.1 / 6.0   ✓ PASS
  Expertise Depth:   5.8 / 6.0   ⚠ WARN (soft threshold)
  Token Budget:      PASS        ✓ PASS
  Script Tests:      PASS        ✓ PASS

──────────────────────────────────────────────────────
  Result: PASS (with warnings)
  Gates: 5 passed, 1 warned, 0 failed

  ⚠ Consider improving expertise depth before deployment
══════════════════════════════════════════════════════
```

## Output Format

```json
{
  "quality_gate": {
    "passed": true,
    "result": "warn",
    "score": 8.2,
    "gates_checked": 6,
    "gates_passed": 5,
    "gates_warned": 1,
    "gates_failed": 0,
    "details": {
      "overall_score": {"value": 8.2, "threshold": 7.0, "result": "pass"},
      "spec_compliance": {"value": 1.0, "threshold": 1.0, "result": "pass"},
      "content_quality": {"value": 7.1, "threshold": 6.0, "result": "pass"},
      "expertise_depth": {"value": 5.8, "threshold": 6.0, "result": "warn"},
      "token_budget": {"value": true, "threshold": true, "result": "pass"},
      "script_tests": {"value": true, "threshold": true, "result": "pass"}
    },
    "message": "Quality gate PASSED with warnings. Consider improving: expertise_depth"
  }
}
```

## Integration

```python
# Final validation before installation
gate_result = check_quality_gate(quality_assessment)

if not gate_result.passed:
    print(f"❌ {gate_result.message}")
    return False

if gate_result.result == GateResult.WARN:
    print(f"⚠️  {gate_result.message}")
    # Optionally ask user to confirm

print(f"✓ {gate_result.message}")
proceed_to_installation()
```

## Threshold Rationale

| Gate | Threshold | Rationale |
|------|-----------|-----------|
| Overall ≥7.0 | Industry standard for "good" | Below 7 risks user frustration |
| Spec 100% | Hard requirement | Non-compliant skills won't load |
| Content ≥6.0 | Minimum usability | Below 6 is confusing/incomplete |
| Expertise ≥6.0 | Value threshold | Generic content wastes time |
| Token Pass | Technical limit | Exceeding causes failures |
| Scripts Pass | Safety | Broken scripts are dangerous |
