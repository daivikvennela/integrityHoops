import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
templates = os.path.join(ROOT, "templates")
static_css = os.path.join(ROOT, "static", "css")

required_templates = [
    "index.html",
    "players.html",
    "player_management_dashboard.html",
]
required_css = [
    "animated-scorecard.css",
    "landing.css",
]


def main() -> None:
    errors = []
    for t in required_templates:
        if not os.path.exists(os.path.join(templates, t)):
            errors.append(f"Missing template: {t}")
    for c in required_css:
        if not os.path.exists(os.path.join(static_css, c)):
            errors.append(f"Missing CSS: {c}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK: templates/static present")


if __name__ == "__main__":
    main()


