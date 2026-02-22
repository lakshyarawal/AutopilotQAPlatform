import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CORE_MODULES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "streamlit",
    "pandas",
    "requests",
]
OPTIONAL_MODULES = ["kafka"]


def check_python() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 10)
    return ok, f"python_version={sys.version.split()[0]}"


def check_modules() -> tuple[bool, str]:
    missing = []
    for module in REQUIRED_CORE_MODULES:
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(module)
    if missing:
        return False, f"missing_modules={','.join(missing)}"
    return True, "all_required_modules_present=true"


def check_optional_modules() -> tuple[bool, str]:
    missing = []
    for module in OPTIONAL_MODULES:
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(module)
    if missing:
        return False, f"optional_missing={','.join(missing)}"
    return True, "optional_modules_present=true"


def check_env() -> tuple[bool, str]:
    path = ROOT / ".env"
    return path.exists(), f"env_file={path}"


def check_data() -> tuple[bool, str]:
    path = ROOT / "data/raw/sample_metadata.jsonl"
    return path.exists(), f"sample_metadata={path}"


def check_db_parent() -> tuple[bool, str]:
    db_path = ROOT / "autopilot.db"
    parent = db_path.parent
    ok = os.access(parent, os.W_OK)
    return ok, f"db_parent_writable={parent}"


def main() -> int:
    checks = {
        "python": check_python(),
        "modules": check_modules(),
        "optional_modules": check_optional_modules(),
        "env": check_env(),
        "data": check_data(),
        "db_parent": check_db_parent(),
    }

    failed = False
    for name, (ok, detail) in checks.items():
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")
        if not ok and name != "optional_modules":
            failed = True

    if failed:
        print("preflight_status=degraded")
        return 1

    print("preflight_status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
