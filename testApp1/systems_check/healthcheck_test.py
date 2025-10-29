import os
import requests


def main() -> None:
    base = os.getenv("BASE_URL", "http://127.0.0.1:5000")
    url = f"{base.rstrip('/')}/healthz"
    r = requests.get(url, timeout=10)
    assert r.status_code == 200, f"/healthz status {r.status_code}"
    print("OK: /healthz 200")


if __name__ == "__main__":
    main()


