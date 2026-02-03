# E2E Testing Patterns Reference

End-to-end testing patterns for Platxa using Kind and Playwright.

## Kind Cluster Setup

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 8080
```

```bash
# Create or reuse cluster
CLUSTER_NAME="${CLUSTER_NAME:-platxa-test}"
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    kind create cluster --name "$CLUSTER_NAME" --config kind-config.yaml
fi
kubectl wait --for=condition=Ready nodes --all --timeout=120s
```

## Cluster Fixtures

```python
import pytest
import subprocess

@pytest.fixture(scope="session")
def kind_cluster():
    cluster_name = "platxa-test"
    result = subprocess.run(["kind", "get", "clusters"], capture_output=True, text=True)
    if cluster_name not in result.stdout:
        subprocess.run(["kind", "create", "cluster", "--name", cluster_name], check=True)
    yield cluster_name
    subprocess.run(["kubectl", "delete", "namespace",
                   "--selector=platxa.com/test=true", "--ignore-not-found"])

@pytest.fixture
def test_namespace(kind_cluster):
    import uuid
    namespace = f"test-{uuid.uuid4().hex[:8]}"
    subprocess.run(["kubectl", "create", "namespace", namespace], check=True)
    subprocess.run(["kubectl", "label", "namespace", namespace, "platxa.com/test=true"], check=True)
    yield namespace
    subprocess.run(["kubectl", "delete", "namespace", namespace, "--ignore-not-found"])
```

## Instance Lifecycle Tests

```python
@pytest.mark.e2e
class TestInstanceLifecycle:
    def test_create_provision_delete(self, test_namespace, k8s_client):
        instance = create_instance(name="e2e-test", namespace=test_namespace)
        instance.provision()
        wait_for_status(instance, "active", timeout=120)
        assert deployment_ready(test_namespace, "odoo-e2e-test")

        instance.suspend()
        wait_for_status(instance, "suspended", timeout=60)

        instance.resume()
        wait_for_status(instance, "active", timeout=120)

        instance.delete()
        wait_for_status(instance, "deleted", timeout=60)
```

## Kubernetes Helpers

```python
from kubernetes import client

def deployment_ready(namespace: str, name: str) -> bool:
    apps_v1 = client.AppsV1Api()
    try:
        deploy = apps_v1.read_namespaced_deployment(name, namespace)
        return deploy.status.ready_replicas is not None and deploy.status.ready_replicas >= 1
    except client.ApiException:
        return False

def wait_for_replicas(namespace: str, name: str, count: int, timeout: int = 120):
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

## Playwright Configuration

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
```

## Visual Tests

```typescript
import { test, expect } from '@playwright/test';

test('editor matches snapshot', async ({ page }) => {
  await page.goto('/editor');
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveScreenshot('editor-default.png', {
    maxDiffPixels: 100,
    animations: 'disabled',
  });
});
```

## CI Pipeline

```yaml
jobs:
  e2e-kind:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: helm/kind-action@v1
      - run: pytest tests/ -m "e2e" -v --timeout=600

  e2e-playwright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: pnpm exec playwright install --with-deps
      - run: pnpm exec playwright test
```

## Running Tests

```bash
# Kind cluster tests
pytest tests/ -m e2e -v --timeout=600

# Playwright tests
pnpm exec playwright test
pnpm exec playwright test --update-snapshots
```
