import os
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
CONFIG_DIR = ROOT_DIR / "config"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR}/ertmac_nwis.db"
)

def load_yaml_config(filename: str) -> dict:
    filepath = CONFIG_DIR / filename
    if not filepath.exists():
        # Fallback search path
        filepath = BASE_DIR / "config" / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

STRATIGRAPHY_CONFIG = load_yaml_config("stratigraphy.yaml")
ALERTS_CONFIG = load_yaml_config("alerts.yaml")
