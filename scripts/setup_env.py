"""Create a local .env file for ESN Forge without committing secrets."""
from __future__ import annotations

from getpass import getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"


def main() -> None:
    if ENV_FILE.exists():
        print(f"{ENV_FILE} already exists. Nothing was changed.")
        return

    print("ESN Forge environment setup")
    print("Enter your local secrets. They will be written only to .env.")
    token = getpass("Discord bot token: ").strip()
    owner_ids = input("Owner Discord user ID(s), comma-separated: ").strip()
    openai_key = getpass("OpenAI API key: ").strip()
    model = input("OpenAI model [gpt-5.6-luna]: ").strip() or "gpt-5.6-luna"

    if not token:
        raise SystemExit("Discord bot token is required.")
    if not owner_ids:
        raise SystemExit("At least one owner ID is required.")
    if not openai_key:
        raise SystemExit("OpenAI API key is required for AI features.")

    content = (
        "# Local ESN Forge configuration -- DO NOT COMMIT THIS FILE.\n"
        f"DISCORD_TOKEN={token}\n"
        f"OWNER_IDS={owner_ids}\n"
        f"OPENAI_API_KEY={openai_key}\n"
        f"OPENAI_MODEL={model}\n"
    )
    ENV_FILE.write_text(content, encoding="utf-8")
    print(f"Created {ENV_FILE}")
    print(".env is ignored by Git and will not be committed.")


if __name__ == "__main__":
    main()
