import os

import pytest
import requests

URLS = {"vuln": os.environ.get("VULN_URL", "http://localhost:5001"),
        "fixed": os.environ.get("FIXED_URL", "http://localhost:5002")}


def pytest_addoption(parser):
    parser.addoption("--target", default="vuln", choices=["vuln", "fixed"])


@pytest.fixture(scope="session")
def base(request):
    url = URLS[request.config.getoption("--target")]
    try:
        requests.get(f"{url}/health", timeout=3)
    except requests.RequestException:
        pytest.exit(f"Brak odpowiedzi z {url}. Uruchomiliście 'docker compose up -d'?", returncode=2)
    return url
