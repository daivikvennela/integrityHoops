import os
import sys
import json


def main() -> None:
    expected = {
        "FLASK_ENV": "production",
        "DEBUG": "False",
    }
    errors = []
    for k, v in expected.items():
        if os.getenv(k) != v:
            errors.append(f"{k} should be {v}, got {os.getenv(k)}")

    upload = os.getenv("UPLOAD_FOLDER")
    processed = os.getenv("PROCESSED_FOLDER")
    if not upload or not processed:
        errors.append("UPLOAD_FOLDER/PROCESSED_FOLDER must be set")

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        sys.exit(1)
    print(json.dumps({"ok": True}, indent=2))


if __name__ == "__main__":
    main()


