import os
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
ROUTES = ["/", "/players", "/smartdash", "/healthz"]


def check(path: str) -> None:
    r = requests.get(BASE.rstrip("/") + path, timeout=15)
    assert r.status_code in (200, 302), f"{path} -> {r.status_code}"


def main() -> None:
    for p in ROUTES:
        check(p)
    print("OK: core routes reachable")


if __name__ == "__main__":
    main()


