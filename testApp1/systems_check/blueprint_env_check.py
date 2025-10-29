import os
import sys
import json
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RENDER_YAML = os.path.join(ROOT, "render.yaml")


def main() -> None:
    with open(RENDER_YAML, "r") as f:
        y = yaml.safe_load(f)

    svc = y["services"][0]
    errors = []

    if svc.get("runtimeVersion") != "3.12.6":
        errors.append(f"runtimeVersion != 3.12.6: {svc.get('runtimeVersion')}")

    build_cmd = svc.get("buildCommand", "")
    if "--only-binary=:all:" not in build_cmd or "testApp1/config/requirements.txt" not in build_cmd:
        errors.append(f"buildCommand missing wheels-only or wrong path: {build_cmd}")

    start_cmd = svc.get("startCommand", "")
    if ("gunicorn" not in start_cmd) or ("0.0.0.0:$PORT" not in start_cmd) or ("src.core.app:app" not in start_cmd):
        errors.append(f"startCommand misconfigured: {start_cmd}")

    # Best-effort environment validation (only present at runtime)
    pip_only = os.getenv("PIP_ONLY_BINARY")
    pyver = os.getenv("PYTHON_VERSION")
    if pip_only is not None and pip_only != ":all:":
        errors.append(f"PIP_ONLY_BINARY should be ':all:', got {pip_only}")
    if pyver is not None and pyver != "3.12.6":
        errors.append(f"PYTHON_VERSION should be 3.12.6, got {pyver}")

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        sys.exit(1)
    print(json.dumps({"ok": True}, indent=2))


if __name__ == "__main__":
    main()


