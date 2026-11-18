"""Project paths and settings, computed from this file's location (no hardcoded folder)."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
VEC_DIR = ROOT / "vector_db"
PROC_DIR = ROOT / "processed_data"
DATA_DIR = ROOT / "data"
APP_DIR = ROOT / "app"

DEFAULT_MODEL = "claude-sonnet-5-5"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def load_env() -> None:
    """Load variables from the repo's .env file (existing env variables win)."""
    load_dotenv(ROOT / ".env")


def get_model_name() -> str:
    """Return the Claude model from CLAUDE_MODEL, or the default."""
    return os.environ.get("CLAUDE_MODEL") or DEFAULT_MODEL
