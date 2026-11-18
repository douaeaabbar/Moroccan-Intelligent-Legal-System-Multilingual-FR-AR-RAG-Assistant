"""Tests de base : vérifient que les données du projet sont présentes et lisibles."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_processed_laws_csv_exists_and_not_empty():
    df = pd.read_csv(ROOT / "processed_laws.csv")
    assert len(df) > 0


def test_vector_db_folder_exists():
    assert (ROOT / "vector_db").is_dir()
