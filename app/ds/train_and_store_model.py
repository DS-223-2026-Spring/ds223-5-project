from __future__ import annotations

from pathlib import Path
import sys

DS_DIR = Path(__file__).resolve().parent
APP_DIR = DS_DIR.parent
sys.path.insert(0, str(DS_DIR))
sys.path.insert(0, str(APP_DIR))

from modeling_pipeline import main_train  # noqa: E402


if __name__ == "__main__":
    main_train()

