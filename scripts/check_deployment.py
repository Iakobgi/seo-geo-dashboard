"""Read-only smoke checks against the same API prefix used by the browser."""
import json
import sys
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def check(base_url):
    for path, expected_status, expected_body in (
        ("/health", 200, {"status": "healthy"}),
        ("/health/ready", 200, {"status": "ready"}),
        ("/auth/me", 401, None),
    ):
        url = base_url.rstrip("/") + path
        try:
            response = urlopen(url, timeout=10)
        except HTTPError as error:
            response = error
        with response:
            assert response.status == expected_status, (
                f"{path}: expected HTTP {expected_status}, got {response.status}"
            )
            assert response.headers.get_content_type() == "application/json", (
                f"{path}: expected JSON from the API"
            )
            body = json.load(response)
            if expected_body is not None:
                assert body == expected_body, f"{path}: unexpected API response"
        print(f"OK {path}")


def test_auth(base_url):
    """Use only against a disposable test database; creates a test user."""
    payload = {"email": f"proxy-{uuid.uuid4().hex}@example.com", "password": "TestPass123!"}

    def request(path, data=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = Request(
            base_url.rstrip("/") + path,
            data=json.dumps(data).encode() if data is not None else None,
            headers=headers,
        )
        with urlopen(req, timeout=10) as response:
            return json.load(response)

    assert request("/auth/register", payload)["email"] == payload["email"]
    token = request("/auth/login", payload)["access_token"]
    assert request("/auth/me", token=token)["email"] == payload["email"]
    print("OK register, login, and authenticated profile through proxy")


if __name__ == "__main__":
    check(sys.argv[1])
    if "--test-auth" in sys.argv[2:]:
        test_auth(sys.argv[1])
