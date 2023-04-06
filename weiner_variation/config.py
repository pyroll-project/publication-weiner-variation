from pathlib import Path

import jinja2

ROOT_DIR = Path(__file__).parent
ROOT_FILE = ROOT_DIR / "weiner_variation.tex"
RC_FILE = ROOT_DIR / "latexmkrc"

DATA_DIR = ROOT_DIR / "data"
SIM_DIR = ROOT_DIR / "sim"
IMG_DIR = ROOT_DIR / "img"
TEX_DIR = ROOT_DIR / "tex"

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT_DIR, encoding="utf-8")
)
