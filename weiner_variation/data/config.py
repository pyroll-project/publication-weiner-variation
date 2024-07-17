from weiner_variation.config import DATA_DIR

MATERIALS = ["c15", "c45"]

IBA_EXPORT_DIR = DATA_DIR / "iba_export"
IBA_EXPORT_FILES = {m: sorted((IBA_EXPORT_DIR / m).glob("*.txt")) for m in MATERIALS}

DATA_STEMS = {m: [f.stem for f in IBA_EXPORT_FILES[m]] for m in IBA_EXPORT_FILES}

RAW_DATA_DIR = DATA_DIR / "raw_data"
RAW_DATA_FILES = {m: [RAW_DATA_DIR / m / f"{s}.csv" for s in DATA_STEMS[m]] for m in DATA_STEMS}

PASSES_DIR = DATA_DIR / "passes"
PASSES_FILES = {m: [PASSES_DIR / m / f"{s}.csv" for s in DATA_STEMS[m]] for m in DATA_STEMS}

PAUSES_BINS = 20
MAX_PAUSE = 15
