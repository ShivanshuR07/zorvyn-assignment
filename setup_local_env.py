from __future__ import annotations

from getpass import getpass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"


def ask(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def ask_secret(prompt: str, default: str) -> str:
    value = getpass(f"{prompt} [{'*' * len(default)}]: ").strip()
    return value or default


def ask_bool(prompt: str, default: bool) -> str:
    label = "true" if default else "false"
    value = input(f"{prompt} [{label}]: ").strip().lower()
    if not value:
        return label
    if value in {"1", "true", "yes", "y", "on"}:
        return "true"
    if value in {"0", "false", "no", "n", "off"}:
        return "false"
    return label


def main() -> int:
    print("Create local .env for the finance dashboard backend")
    print(f"Target file: {ENV_PATH}")
    print()

    db_host = ask("PostgreSQL host", "localhost")
    db_port = ask("PostgreSQL port", "5432")
    db_name = ask("Database name", "finance_dashboard")
    db_user = ask("Database user", "postgres")
    db_password = ask_secret("Database password", "postgres")
    jwt_secret = ask_secret("JWT secret key", "change-this-secret")
    jwt_algorithm = ask("JWT algorithm", "HS256")
    jwt_expire = ask("JWT expire minutes", "60")
    app_env = ask("App environment", "development")
    debug = ask_bool("Debug mode", True)
    cors_origins = ask("CORS origins", "http://localhost:3000,http://localhost:5173")

    env_text = "\n".join(
        [
            f"DATABASE_URL=postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
            f"JWT_SECRET_KEY={jwt_secret}",
            f"JWT_ALGORITHM={jwt_algorithm}",
            f"JWT_EXPIRE_MINUTES={jwt_expire}",
            f"APP_ENV={app_env}",
            f"DEBUG={debug}",
            f"CORS_ORIGINS={cors_origins}",
            "",
        ]
    )

    ENV_PATH.write_text(env_text, encoding="utf-8")

    print()
    print(f"Wrote {ENV_PATH}")
    print("Next steps:")
    print("  1. Restart the backend if it is running.")
    print("  2. Run: alembic upgrade head")
    print("  3. Run: python -m scripts.seed")
    print("  4. Run: python run_full_stack.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
