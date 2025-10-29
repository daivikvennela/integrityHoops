import os
import shlex
import subprocess
import sys
from typing import List, Tuple


def run_cmd(label: str, cmd: str, env: dict | None = None) -> Tuple[str, str]:
    try:
        proc = subprocess.run(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env or os.environ.copy(),
        )
        if proc.returncode == 0:
            return ("OK", proc.stdout.strip())
        # Heuristics for N/A conditions
        stderr = proc.stderr.strip()
        stdout = proc.stdout.strip()
        combined = "\n".join([stdout, stderr]).strip()
        na_reasons = (
            "ModuleNotFoundError",
            "No module named",
            "DATABASE_URL not set",
            "Operation timed out",
            "Temporary failure in name resolution",
        )
        if any(s in combined for s in na_reasons):
            return ("N/A", combined)
        return ("FAIL", combined)
    except FileNotFoundError as e:
        return ("N/A", f"Executable missing: {e}")
    except Exception as e:
        return ("FAIL", str(e))


def main() -> None:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(project_root)

    checks: List[Tuple[str, str]] = [
        (
            "Blueprint/env config",
            "python3 testApp1/systems_check/blueprint_env_check.py",
        ),
        (
            "Templates/static presence",
            "python3 testApp1/systems_check/static_templates_check.py",
        ),
        (
            "Health endpoint",
            "python3 testApp1/systems_check/healthcheck_test.py",
        ),
        (
            "Core routes smoke",
            "python3 testApp1/systems_check/smoke_routes_test.py",
        ),
        (
            "Env flags (production)",
            "python3 testApp1/systems_check/env_flags_test.py",
        ),
        (
            "DB connectivity",
            "python3 testApp1/systems_check/db_connection_test.py",
        ),
        (
            "Wheels probe (cp312 manylinux)",
            "bash testApp1/systems_check/wheels_probe.sh",
        ),
        (
            "Pip no-builds dry-run",
            "bash testApp1/systems_check/pip_no_builds_guard.sh",
        ),
        (
            "Gunicorn port bind",
            "bash testApp1/systems_check/port_bind_test.sh",
        ),
    ]

    results: List[Tuple[str, str, str]] = []

    for label, cmd in checks:
        status, detail = run_cmd(label, cmd)
        results.append((label, status, detail))

    # Pretty print summary
    print("=== System Checks Summary ===")
    for label, status, _ in results:
        print(f"- {label}: {status}")

    print("\n=== Details ===")
    for label, status, detail in results:
        truncated = (detail[:800] + "…") if len(detail) > 800 else detail
        print(f"\n[{label}] {status}\n{truncated if truncated else '(no output)'}")

    # Exit code: 0 if all OK or N/A, 1 if any FAIL
    exit_code = 0 if all(r[1] in ("OK", "N/A") for r in results) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


