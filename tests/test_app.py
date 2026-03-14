import pytest
from src.app import app


@pytest.fixture
def client():
    """Create a test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test the health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_list_vulnerabilities(client):
    """Test listing all vulns."""
    response = client.get("/api/v1/vulns")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 3


def test_get_vulnerability(client):
    """Test looking up a specific CVE."""
    response = client.get("/api/v1/vulns/CVE-2024-1234")
    assert response.status_code == 200
    data = response.get_json()
    assert data["severity"] == "HIGH"


def test_get_vulnerability_not_found(client):
    """Test 404 for unknown CVE."""
    response = client.get("/api/v1/vulns/CVE-0000-0000")
    assert response.status_code == 404


def test_filter_by_severity(client):
    """Test filtering by severity level."""
    response = client.get("/api/v1/vulns?severity=CRITICAL")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 1