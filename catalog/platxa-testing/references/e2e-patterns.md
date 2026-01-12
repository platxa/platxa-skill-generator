# E2E Testing Patterns Reference

End-to-end testing patterns for Platxa using Kind, Playwright, and instance lifecycle tests.

## Kind Cluster Setup

### Cluster Configuration

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 8080
        protocol: TCP
      - containerPort: 30443
        hostPort: 8443
        protocol: TCP
```

### Cluster Management Scripts

```bash
#!/bin/bash
# scripts/cluster-setup.sh

CLUSTER_NAME="${CLUSTER_NAME:-platxa-test}"

# Create or reuse cluster
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Reusing existing cluster: ${CLUSTER_NAME}"
else
    kind create cluster --name "$CLUSTER_NAME" --config kind-config.yaml
fi

# Wait for cluster ready
kubectl wait --for=condition=Ready nodes --all --timeout=120s
```

```bash
#!/bin/bash
# scripts/cluster-cleanup.sh

CLUSTER_NAME="${CLUSTER_NAME:-platxa-test}"

# Delete test namespaces only (preserve cluster)
kubectl delete namespace --selector=platxa.com/test=true --ignore-not-found

# Optional: full cleanup
# kind delete cluster --name "$CLUSTER_NAME"
```

## Cluster Health Fixtures

```python
import pytest
import subprocess
from typing import Generator

@pytest.fixture(scope="session")
def kind_cluster() -> Generator[str, None, None]:
    """Ensure Kind cluster is running for test session."""
    cluster_name = "platxa-test"

    # Create if not exists
    result = subprocess.run(
        ["kind", "get", "clusters"],
        capture_output=True, text=True
    )

    if cluster_name not in result.stdout:
        subprocess.run([
            "kind", "create", "cluster",
            "--name", cluster_name,
            "--config", "kind-config.yaml"
        ], check=True)

    yield cluster_name

    # Cleanup test namespaces (not cluster)
    subprocess.run([
        "kubectl", "delete", "namespace",
        "--selector=platxa.com/test=true",
        "--ignore-not-found"
    ])

@pytest.fixture
def test_namespace(kind_cluster: str) -> Generator[str, None, None]:
    """Create isolated test namespace."""
    import uuid
    namespace = f"test-{uuid.uuid4().hex[:8]}"

    subprocess.run([
        "kubectl", "create", "namespace", namespace,
        "--context", f"kind-{kind_cluster}"
    ], check=True)

    subprocess.run([
        "kubectl", "label", "namespace", namespace,
        "platxa.com/test=true",
        "--context", f"kind-{kind_cluster}"
    ], check=True)

    yield namespace

    subprocess.run([
        "kubectl", "delete", "namespace", namespace,
        "--context", f"kind-{kind_cluster}",
        "--ignore-not-found"
    ])
```

## Instance Lifecycle Tests

```python
@pytest.mark.e2e
class TestInstanceLifecycle:
    """E2E tests for complete instance lifecycle."""

    def test_create_provision_delete(self, test_namespace, k8s_client):
        """Feature #1: Full instance lifecycle."""
        # 1. Create instance record
        instance = create_instance(
            name="e2e-test",
            namespace=test_namespace
        )
        assert instance.status == "draft"

        # 2. Provision (creates K8s resources)
        instance.provision()
        wait_for_status(instance, "active", timeout=120)

        # 3. Verify K8s resources exist
        assert namespace_exists(test_namespace)
        assert deployment_ready(test_namespace, "odoo-e2e-test")
        assert service_exists(test_namespace, "odoo-e2e-test")

        # 4. Suspend instance
        instance.suspend()
        wait_for_status(instance, "suspended", timeout=60)
        assert deployment_replicas(test_namespace, "odoo-e2e-test") == 0

        # 5. Resume instance
        instance.resume()
        wait_for_status(instance, "active", timeout=120)
        assert deployment_replicas(test_namespace, "odoo-e2e-test") >= 1

        # 6. Delete instance
        instance.delete()
        wait_for_status(instance, "deleted", timeout=60)

    def test_wake_from_zero(self, test_namespace, k8s_client):
        """Feature #2: Scale-to-zero wake functionality."""
        instance = create_and_provision_instance(test_namespace)

        # Scale to zero
        scale_deployment(test_namespace, "odoo", 0)
        wait_for_replicas(test_namespace, "odoo", 0)

        # Trigger wake via HTTP
        response = requests.get(f"https://{instance.hostname}/")

        # Should wake and respond
        assert response.status_code == 200
        assert deployment_replicas(test_namespace, "odoo") >= 1
```

## Kubernetes Helpers

```python
from kubernetes import client, config

def namespace_exists(name: str) -> bool:
    """Check if namespace exists."""
    v1 = client.CoreV1Api()
    try:
        v1.read_namespace(name)
        return True
    except client.ApiException as e:
        if e.status == 404:
            return False
        raise

def deployment_ready(namespace: str, name: str) -> bool:
    """Check if deployment is ready."""
    apps_v1 = client.AppsV1Api()
    try:
        deploy = apps_v1.read_namespaced_deployment(name, namespace)
        return (
            deploy.status.ready_replicas is not None
            and deploy.status.ready_replicas >= 1
        )
    except client.ApiException:
        return False

def wait_for_replicas(namespace: str, name: str, count: int, timeout: int = 120):
    """Wait for deployment to reach replica count."""
    import time
    apps_v1 = client.AppsV1Api()
    start = time.time()

    while time.time() - start < timeout:
        deploy = apps_v1.read_namespaced_deployment(name, namespace)
        if deploy.status.ready_replicas == count:
            return
        time.sleep(2)

    raise TimeoutError(f"Deployment {name} did not reach {count} replicas")
```

## Playwright Visual Testing

### Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
});
```

### Visual Regression Tests

```typescript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('editor matches snapshot', async ({ page }) => {
    await page.goto('/editor');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('editor-default.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
      animations: 'disabled',
    });
  });

  test('button states match snapshots', async ({ page }) => {
    await page.goto('/components/button');

    const button = page.locator('button.primary');

    // Default state
    await expect(button).toHaveScreenshot('button-default.png');

    // Hover state
    await button.hover();
    await expect(button).toHaveScreenshot('button-hover.png');

    // Focus state
    await button.focus();
    await expect(button).toHaveScreenshot('button-focus.png');
  });
});
```

### Interaction Tests

```typescript
test.describe('User Interactions', () => {
  test('login flow completes successfully', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Welcome');
  });
});
```

## CI Pipeline

```yaml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  e2e-kind:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: helm/kind-action@v1
        with:
          cluster_name: platxa-test
      - run: pip install pytest kubernetes
      - run: pytest tests/ -m "e2e" -v --timeout=600

  e2e-playwright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
      - run: pnpm install
      - run: pnpm exec playwright install --with-deps
      - run: pnpm exec playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## Running E2E Tests

```bash
# Kind cluster tests
pytest tests/ -m e2e -v --timeout=600

# Playwright tests
pnpm exec playwright test

# With visual snapshots update
pnpm exec playwright test --update-snapshots

# Specific browser
pnpm exec playwright test --project=chromium
```

