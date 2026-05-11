"""Interactive setup for Schwab environment variables."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .env import ENV_VARS, LOWERCASE_FALLBACKS, read_env_value, redacted


def _valid_secret(value: str) -> bool:
    return value.isalnum() and len(value) >= 10


def _valid_callback(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _valid_token_path(value: str) -> bool:
    if not value.strip():
        return False
    parent = Path(value).expanduser().resolve().parent
    return parent.exists()


VAR_INFO = {
    "SCHWAB_API_KEY": ("Your Schwab API key", _valid_secret),
    "SCHWAB_APP_SECRET": ("Your Schwab app secret", _valid_secret),
    "SCHWAB_CALLBACK_URL": ("Your Schwab OAuth callback URL", _valid_callback),
    "SCHWAB_TOKEN_PATH": ("Path to your existing/shared Schwab token file", _valid_token_path),
}


def persist_env(name: str, value: str) -> None:
    """Persist an environment variable for the current user."""

    if platform.system() == "Windows":
        subprocess.run(["setx", name, value], check=True)
        return

    shell = os.environ.get("SHELL", "")
    rcfile = Path.home() / (".zshrc" if shell.endswith("zsh") else ".bashrc")
    existing = rcfile.read_text(encoding="utf-8").splitlines() if rcfile.exists() else []
    prefix = f"export {name}="
    lines = [line for line in existing if not line.strip().startswith(prefix)]
    lines.append(f'export {name}="{value}"')
    rcfile.write_text("\n".join(lines) + "\n", encoding="utf-8")


def show_env() -> None:
    for name in ENV_VARS:
        value = read_env_value(name)
        source = name if os.getenv(name) else LOWERCASE_FALLBACKS[name]
        if value:
            print(f"{name} = {redacted(value)} (source: {source})")
        else:
            print(f"{name} is not set")


def prompt_var(name: str) -> None:
    description, validator = VAR_INFO[name]
    existing = read_env_value(name)
    if existing:
        print(f"\n{name} is set to {redacted(existing)}")
        if input("Change it? [y/N]: ").strip().lower() != "y":
            return
    else:
        if input(f"\n{name} is not set. Create it now? [Y/n]: ").strip().lower() == "n":
            return

    while True:
        value = input(f"Enter {description}: ").strip()
        if validator(value):
            persist_env(name, value)
            os.environ[name] = value
            print(f"{name} set.")
            return
        print(f"Invalid {name}.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Schwab environment variables.")
    parser.add_argument("--show", action="store_true", help="Show current Schwab env vars.")
    args = parser.parse_args(argv)

    if args.show:
        show_env()
        return 0

    print("This utility configures Schwab environment variables for this user.")
    print("SCHWAB_TOKEN_PATH is shared with other apps; keep the existing path unless you mean to change it.")
    for name in ENV_VARS:
        prompt_var(name)
    print("Done. Open a new shell for persisted variables to be available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
