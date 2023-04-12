from pathlib import Path

ROOT_DIR = Path(__file__).parent
ROOT_FILE = ROOT_DIR / "weiner_variation.tex"
RC_FILE = ROOT_DIR / "latexmkrc"

DATA_DIR = ROOT_DIR / "data"
SIM_DIR = ROOT_DIR / "sim"
IMG_DIR = ROOT_DIR / "img"
SECTIONS_DIR = ROOT_DIR / "sections"

BUILD_DIR = ROOT_DIR / ".build"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
