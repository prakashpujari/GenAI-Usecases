from __future__ import annotations

from dotenv import load_dotenv

from src.config import load_settings
from src.pipeline import run_pipeline


def main() -> None:
    load_dotenv()
    settings = load_settings()
    run_pipeline(settings)


if __name__ == "__main__":
    main()
