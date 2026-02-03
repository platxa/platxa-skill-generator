"""Tests for score-skill.py — multi-dimension scoring and badge assignment.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from helpers import create_executable_script, create_reference_file, create_skill_md


@pytest.fixture
def run_score_skill(scripts_dir: Path):
    """Fixture to run score-skill.py via subprocess."""
    script_path = scripts_dir / "score-skill.py"

    def _run(
        skill_dir: Path,
        *,
        json_output: bool = True,
        threshold: float | None = None,
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path)]
        if json_output:
            cmd.append("--json")
        if threshold is not None:
            cmd.extend(["--threshold", str(threshold)])
        cmd.append(str(skill_dir))
        return subprocess.run(cmd, capture_output=True, text=True)

    return _run


def _create_rich_skill(base: Path, name: str = "rich-skill") -> Path:
    """Create a high-quality skill designed to score well across all dimensions."""
    skill_dir = base / name
    skill_dir.mkdir()

    refs_dir = skill_dir / "references"
    refs_dir.mkdir()

    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: rich-skill\n"
        "description: Kubernetes deployment automation with rolling updates, "
        "health checks, and resource management for production workloads\n"
        "tools:\n"
        "  - Read\n"
        "  - Write\n"
        "  - Bash\n"
        "  - Grep\n"
        "metadata:\n"
        "  version: '2.1.0'\n"
        "  author: Platform Team\n"
        "  tags:\n"
        "    - kubernetes\n"
        "    - deployment\n"
        "    - infrastructure\n"
        "---\n"
        "\n"
        "# Kubernetes Deployment Automation\n"
        "\n"
        "Use when deploying services to Kubernetes clusters with "
        "zero-downtime rolling updates.\n"
        "\n"
        "## Workflow\n"
        "\n"
        "1. Validate manifests with `kubectl apply --dry-run=client`\n"
        "2. Apply Deployment with rolling update strategy\n"
        "3. Monitor rollout status via `kubectl rollout status`\n"
        "4. Verify health endpoints respond with HTTP 200\n"
        "\n"
        "## Examples\n"
        "\n"
        "### Deploy with resource limits\n"
        "\n"
        "```yaml\n"
        "apiVersion: apps/v1\n"
        "kind: Deployment\n"
        "metadata:\n"
        "  name: api-server\n"
        "  namespace: production\n"
        "spec:\n"
        "  replicas: 3\n"
        "  strategy:\n"
        "    type: RollingUpdate\n"
        "    rollingUpdate:\n"
        "      maxSurge: 1\n"
        "      maxUnavailable: 0\n"
        "  template:\n"
        "    spec:\n"
        "      containers:\n"
        "        - name: api\n"
        "          image: registry.example.com/api:v2.1.0\n"
        "          resources:\n"
        "            requests:\n"
        "              memory: 256Mi\n"
        "              cpu: 100m\n"
        "            limits:\n"
        "              memory: 512Mi\n"
        "              cpu: 500m\n"
        "          livenessProbe:\n"
        "            httpGet:\n"
        "              path: /healthz\n"
        "              port: 8080\n"
        "            initialDelaySeconds: 15\n"
        "            periodSeconds: 10\n"
        "```\n"
        "\n"
        "### Scale with HPA\n"
        "\n"
        "```yaml\n"
        "apiVersion: autoscaling/v2\n"
        "kind: HorizontalPodAutoscaler\n"
        "metadata:\n"
        "  name: api-hpa\n"
        "spec:\n"
        "  scaleTargetRef:\n"
        "    apiVersion: apps/v1\n"
        "    kind: Deployment\n"
        "    name: api-server\n"
        "  minReplicas: 2\n"
        "  maxReplicas: 10\n"
        "  metrics:\n"
        "    - type: Resource\n"
        "      resource:\n"
        "        name: cpu\n"
        "        target:\n"
        "          type: Utilization\n"
        "          averageUtilization: 70\n"
        "```\n"
        "\n"
        "### Verify rollout\n"
        "\n"
        "```bash\n"
        "kubectl rollout status deployment/api-server -n production --timeout=300s\n"
        "kubectl get pods -n production -l app=api-server -o wide\n"
        "kubectl top pods -n production -l app=api-server\n"
        "```\n"
        "\n"
        "## Output Checklist\n"
        "\n"
        "- Deployment manifest validated with dry-run\n"
        "- Rolling update completed with zero downtime\n"
        "- All pods report Ready status within 5min timeout\n"
        "- HPA configured with CPU threshold at 70%\n"
        "- Resource requests set: 256Mi memory, 100m CPU\n"
        "- Resource limits set: 512Mi memory, 500m CPU\n"
    )

    create_reference_file(
        refs_dir,
        "rollout-patterns.md",
        "# Rollout Patterns\n\n"
        "## Blue-Green Deployment\n\n"
        "Deploy new version alongside old, switch Service selector.\n\n"
        "## Canary Release\n\n"
        "Route 10% traffic to new version via Istio VirtualService weight.\n\n"
        "## Rolling Update\n\n"
        "Default K8s strategy with maxSurge=1, maxUnavailable=0.\n",
    )
    create_reference_file(
        refs_dir,
        "troubleshooting.md",
        "# Troubleshooting Guide\n\n"
        "## CrashLoopBackOff\n\n"
        "Check logs: `kubectl logs pod-name -n namespace --previous`\n"
        "Common causes: OOMKilled, missing config, port conflicts.\n\n"
        "## ImagePullBackOff\n\n"
        "Verify image exists: `docker manifest inspect image:tag`\n"
        "Check pull secrets: `kubectl get secrets -n namespace`\n",
    )
    create_reference_file(
        refs_dir,
        "monitoring.md",
        "# Monitoring\n\n"
        "## Prometheus Metrics\n\n"
        "- `kube_deployment_status_replicas_available`\n"
        "- `container_memory_usage_bytes`\n"
        "- `container_cpu_usage_seconds_total`\n\n"
        "## Alert Rules\n\n"
        "Fire alert when available replicas < desired for 5min.\n",
    )

    create_executable_script(
        scripts_dir,
        "deploy.sh",
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        'NAMESPACE="${1:-production}"\n'
        'kubectl apply -f manifests/ -n "$NAMESPACE" --dry-run=client\n'
        'kubectl apply -f manifests/ -n "$NAMESPACE"\n'
        'kubectl rollout status deployment -n "$NAMESPACE" --timeout=300s\n'
        'echo "Deployment complete"\n',
    )

    return skill_dir


def _create_minimal_skill(base: Path, name: str = "minimal-skill") -> Path:
    """Create a minimal skill with bare minimum content."""
    skill_dir = base / name
    skill_dir.mkdir()
    create_skill_md(skill_dir, name, "A minimal skill.", content="# Minimal\n\nBasic.\n")
    return skill_dir


# ── Output structure ──────────────────────────────────────────────


class TestOutputStructure:
    """Tests for JSON output structure."""

    @pytest.mark.score
    def test_json_has_required_fields(self, tmp_path: Path, run_score_skill) -> None:
        """JSON output contains skill_name, overall_score, passed, badge, threshold, dimensions."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert "skill_name" in data
        assert "overall_score" in data
        assert "passed" in data
        assert "badge" in data
        assert "threshold" in data
        assert "dimensions" in data

    @pytest.mark.score
    def test_all_six_dimensions_present(self, tmp_path: Path, run_score_skill) -> None:
        """Dimensions dict contains all 6 scoring dimensions."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        expected = {"spec", "content", "structure", "tokens", "completeness", "expertise"}
        assert set(data["dimensions"].keys()) == expected

    @pytest.mark.score
    def test_each_dimension_has_score_weight_notes(self, tmp_path: Path, run_score_skill) -> None:
        """Each dimension entry has score, weight, and notes fields."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        for dim_name, dim_data in data["dimensions"].items():
            assert "score" in dim_data, f"Missing score in {dim_name}"
            assert "weight" in dim_data, f"Missing weight in {dim_name}"
            assert "notes" in dim_data, f"Missing notes in {dim_name}"
            assert isinstance(dim_data["score"], (int, float))
            assert isinstance(dim_data["weight"], (int, float))
            assert isinstance(dim_data["notes"], list)

    @pytest.mark.score
    def test_dimension_scores_in_range(self, tmp_path: Path, run_score_skill) -> None:
        """Each dimension score is between 0 and 10."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        for dim_name, dim_data in data["dimensions"].items():
            assert 0.0 <= dim_data["score"] <= 10.0, f"{dim_name} score out of range"

    @pytest.mark.score
    def test_dimension_weights_sum_to_one(self, tmp_path: Path, run_score_skill) -> None:
        """Dimension weights sum to 1.0."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        total_weight = sum(d["weight"] for d in data["dimensions"].values())
        assert abs(total_weight - 1.0) < 0.001


# ── Spec dimension ────────────────────────────────────────────────


class TestSpecDimension:
    """Tests for spec (frontmatter compliance) scoring."""

    @pytest.mark.score
    def test_complete_frontmatter_scores_high(self, tmp_path: Path, run_score_skill) -> None:
        """Valid name + description + tools + metadata with version yields high spec score."""
        skill_dir = tmp_path / "spec-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: spec-skill\ndescription: Full spec compliance test\n"
            "tools:\n  - Read\n  - Write\n"
            "metadata:\n  version: '1.0'\n---\n\n# Content\n"
        )
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["spec"]["score"] >= 8.0

    @pytest.mark.score
    def test_missing_skill_md_scores_zero(self, tmp_path: Path, run_score_skill) -> None:
        """Missing SKILL.md yields spec score 0."""
        skill_dir = tmp_path / "empty"
        skill_dir.mkdir()
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["spec"]["score"] == 0.0

    @pytest.mark.score
    def test_missing_name_noted(self, tmp_path: Path, run_score_skill) -> None:
        """SKILL.md without name field produces a note about missing name."""
        skill_dir = tmp_path / "no-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: Has description but no name\n---\n\n# Content\n"
        )
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["spec"]["score"] < 7.0
        assert any("name" in n.lower() for n in data["dimensions"]["spec"]["notes"])

    @pytest.mark.score
    def test_invalid_tools_noted(self, tmp_path: Path, run_score_skill) -> None:
        """Invalid tool names in frontmatter produce a note."""
        skill_dir = tmp_path / "bad-tools"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: bad-tools\ndescription: d\n"
            "tools:\n  - Read\n  - FakeTool\n---\n\n# Content\n"
        )
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert any("invalid" in n.lower() for n in data["dimensions"]["spec"]["notes"])


# ── Content dimension ─────────────────────────────────────────────


class TestContentDimension:
    """Tests for content quality scoring."""

    @pytest.mark.score
    def test_rich_content_scores_high(self, tmp_path: Path, run_score_skill) -> None:
        """Body with headers, code blocks, lists, and usage guidance scores well."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["content"]["score"] >= 7.0

    @pytest.mark.score
    def test_placeholder_text_penalized(self, tmp_path: Path, run_score_skill) -> None:
        """TODO and placeholder markers reduce content score and produce notes."""
        skill_dir = tmp_path / "placeholder-skill"
        skill_dir.mkdir()
        create_skill_md(
            skill_dir,
            "placeholder-skill",
            "A skill with placeholder content for testing quality scoring",
            content=(
                "# Placeholder Skill\n\n"
                "TODO: Add real content here\n\n"
                "## Usage\n\n"
                "TBD - describe the usage pattern\n\n"
                "## Examples\n\n"
                "FIXME: Add actual code examples\n\n"
                "[Insert your configuration here]\n"
            ),
        )
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        notes = data["dimensions"]["content"]["notes"]
        assert any("placeholder" in n.lower() for n in notes)

    @pytest.mark.score
    def test_empty_body_scores_zero(self, tmp_path: Path, run_score_skill) -> None:
        """SKILL.md with frontmatter but empty body scores 0 for content."""
        skill_dir = tmp_path / "empty-body"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: empty-body\ndescription: d\n---\n")
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["content"]["score"] == 0.0

    @pytest.mark.score
    def test_slop_patterns_penalized(self, tmp_path: Path, run_score_skill) -> None:
        """AI-generated filler phrases produce notes about generic content."""
        skill_dir = tmp_path / "slop-skill"
        skill_dir.mkdir()
        create_skill_md(
            skill_dir,
            "slop-skill",
            "A comprehensive guide to leveraging state-of-the-art solutions",
            content=(
                "# Slop Skill\n\n"
                "It is important to note that this skill helps you to achieve "
                "seamless integration with robust and scalable systems.\n\n"
                "## Usage\n\n"
                "This skill was designed to leverage the power of modern tools.\n\n"
                "## Examples\n\n"
                "Simply use this skill to get world-class results.\n\n"
                "A comprehensive guide to best practices for ensuring quality.\n"
            ),
        )
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        notes = data["dimensions"]["content"]["notes"]
        assert any("filler" in n.lower() or "generic" in n.lower() for n in notes)


# ── Structure dimension ───────────────────────────────────────────


class TestStructureDimension:
    """Tests for directory structure scoring."""

    @pytest.mark.score
    def test_complete_structure_scores_high(self, tmp_path: Path, run_score_skill) -> None:
        """SKILL.md + references/ with files + scripts/ with executables scores high."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["structure"]["score"] >= 8.0

    @pytest.mark.score
    def test_skill_md_only_gets_base_score(self, tmp_path: Path, run_score_skill) -> None:
        """Just SKILL.md in a directory gives base structure score (5.0)."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["structure"]["score"] == 5.0

    @pytest.mark.score
    def test_non_executable_script_noted(self, tmp_path: Path, run_score_skill) -> None:
        """Non-executable script files produce a note."""
        skill_dir = tmp_path / "noexec-skill"
        skill_dir.mkdir()
        create_skill_md(skill_dir, "noexec-skill", "d")
        scripts = skill_dir / "scripts"
        scripts.mkdir()
        create_executable_script(scripts, "run.sh", "#!/bin/bash\necho ok", executable=False)

        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert any(
            "executable" in n.lower() or "non-exec" in n.lower()
            for n in data["dimensions"]["structure"]["notes"]
        )


# ── Tokens dimension ──────────────────────────────────────────────


class TestTokensDimension:
    """Tests for token budget compliance scoring."""

    @pytest.mark.score
    def test_small_skill_scores_high(self, tmp_path: Path, run_score_skill) -> None:
        """Skill well under token limits scores near 10."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["tokens"]["score"] >= 9.0

    @pytest.mark.score
    def test_rich_skill_still_within_budget(self, tmp_path: Path, run_score_skill) -> None:
        """A well-crafted rich skill stays within token budgets."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["tokens"]["score"] >= 8.0


# ── Completeness dimension ────────────────────────────────────────


class TestCompletenessDimension:
    """Tests for completeness/richness scoring."""

    @pytest.mark.score
    def test_full_metadata_scores_high(self, tmp_path: Path, run_score_skill) -> None:
        """Skill with tags, version, author, references, scripts, sections scores well."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["completeness"]["score"] >= 8.0

    @pytest.mark.score
    def test_minimal_skill_scores_low(self, tmp_path: Path, run_score_skill) -> None:
        """Minimal skill without metadata/references/scripts scores poorly."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["completeness"]["score"] < 4.0


# ── Expertise dimension ───────────────────────────────────────────


class TestExpertiseDimension:
    """Tests for domain expertise scoring."""

    @pytest.mark.score
    def test_technical_content_scores_higher(self, tmp_path: Path, run_score_skill) -> None:
        """Content with specific terms, code blocks, file paths scores well."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["expertise"]["score"] >= 5.0

    @pytest.mark.score
    def test_generic_prose_scores_lower(self, tmp_path: Path, run_score_skill) -> None:
        """Generic text without technical terms or specifics scores low."""
        skill_dir = tmp_path / "generic-skill"
        skill_dir.mkdir()
        create_skill_md(
            skill_dir,
            "generic-skill",
            "A skill that does things with stuff in a general way",
            content=(
                "# Generic Skill\n\n"
                "This skill helps you do things better and more easily.\n\n"
                "It makes your work simpler and faster every single day.\n\n"
                "You can use this skill to improve your overall results.\n"
            ),
        )
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["dimensions"]["expertise"]["score"] < 4.0


# ── Badge assignment ──────────────────────────────────────────────


class TestBadgeAssignment:
    """Tests for badge thresholds via CLI output."""

    @pytest.mark.score
    def test_high_quality_skill_gets_reviewed(self, tmp_path: Path, run_score_skill) -> None:
        """A skill scoring >= 8.0 gets Reviewed badge (Verified requires security context)."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        # CLI doesn't pass security_passed, so max achievable badge is "Reviewed"
        assert data["overall_score"] >= 7.0
        assert data["badge"] == "Reviewed"

    @pytest.mark.score
    def test_low_quality_skill_gets_flagged(self, tmp_path: Path, run_score_skill) -> None:
        """A skill scoring < 5.0 gets Flagged badge."""
        skill_dir = tmp_path / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: bad-skill\ndescription: d\n---\n")
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["overall_score"] < 5.0
        assert data["badge"] == "Flagged"

    @pytest.mark.score
    def test_medium_quality_gets_unverified(self, tmp_path: Path, run_score_skill) -> None:
        """A skill scoring 5.0-7.0 gets Unverified badge."""
        skill_dir = tmp_path / "medium-skill"
        skill_dir.mkdir()
        create_skill_md(
            skill_dir,
            "medium-skill",
            "A medium quality skill for testing badge assignment thresholds",
            tools=["Read", "Write"],
            content=(
                "# Medium Skill\n\n"
                "This skill provides moderate functionality.\n\n"
                "## Usage\n\n"
                "Use when you need to do something.\n\n"
                "## Steps\n\n"
                "1. First do this\n"
                "2. Then do that\n"
                "3. Finally check the result\n\n"
                "## Examples\n\n"
                "```bash\n"
                "echo 'example command'\n"
                "```\n"
            ),
        )
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md", "# Guide\n\nSome reference content.\n")

        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert 5.0 <= data["overall_score"] < 7.0, (
            f"Score {data['overall_score']} not in Unverified range"
        )
        assert data["badge"] == "Unverified"


# ── Threshold and pass/fail ───────────────────────────────────────


class TestThresholdAndPassFail:
    """Tests for threshold configuration and exit code behavior."""

    @pytest.mark.score
    def test_default_threshold_is_seven(self, tmp_path: Path, run_score_skill) -> None:
        """Default passing threshold is 7.0."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["threshold"] == 7.0

    @pytest.mark.score
    def test_custom_threshold_changes_pass(self, tmp_path: Path, run_score_skill) -> None:
        """--threshold 10.0 causes a high-scoring skill to fail."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir, threshold=10.0)
        data = json.loads(result.stdout)

        assert data["threshold"] == 10.0
        assert data["passed"] is False
        assert result.returncode == 1

    @pytest.mark.score
    def test_exit_code_zero_when_passed(self, tmp_path: Path, run_score_skill) -> None:
        """Exit code 0 when skill passes threshold."""
        skill_dir = _create_rich_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["passed"] is True
        assert result.returncode == 0

    @pytest.mark.score
    def test_exit_code_one_when_failed(self, tmp_path: Path, run_score_skill) -> None:
        """Exit code 1 when skill fails threshold."""
        skill_dir = tmp_path / "bad"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: bad\ndescription: d\n---\n")
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["passed"] is False
        assert result.returncode == 1

    @pytest.mark.score
    def test_overall_is_weighted_average(self, tmp_path: Path, run_score_skill) -> None:
        """Overall score equals weighted sum of dimension scores."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        weighted_sum = sum(d["score"] * d["weight"] for d in data["dimensions"].values())
        assert abs(data["overall_score"] - round(weighted_sum, 2)) < 0.01

    @pytest.mark.score
    def test_human_readable_output(self, tmp_path: Path, run_score_skill) -> None:
        """Non-JSON output contains dimension names and overall score."""
        skill_dir = _create_minimal_skill(tmp_path)
        result = run_score_skill(skill_dir, json_output=False)

        assert "spec" in result.stdout
        assert "content" in result.stdout
        assert "structure" in result.stdout
        assert "tokens" in result.stdout
        assert "completeness" in result.stdout
        assert "expertise" in result.stdout
        assert "Overall" in result.stdout


# ── Edge cases ────────────────────────────────────────────────────


class TestEdgeCases:
    """Tests for error handling edge cases."""

    @pytest.mark.score
    def test_not_a_directory_returns_error(self, tmp_path: Path, run_score_skill) -> None:
        """Passing a non-directory path returns exit 1 with error message."""
        result = run_score_skill(tmp_path / "nonexistent")

        assert result.returncode == 1
        assert "not a directory" in result.stderr.lower() or "error" in result.stderr.lower()

    @pytest.mark.score
    def test_skill_name_from_directory(self, tmp_path: Path, run_score_skill) -> None:
        """skill_name in output matches the directory name."""
        skill_dir = _create_minimal_skill(tmp_path, name="my-custom-skill")
        result = run_score_skill(skill_dir)
        data = json.loads(result.stdout)

        assert data["skill_name"] == "my-custom-skill"
