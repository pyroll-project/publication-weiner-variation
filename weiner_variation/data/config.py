from weiner_variation.config import DATA_DIR

IBA_EXPORT_DIR = DATA_DIR / "iba_export"
IBA_EXPORT_FILES = list(IBA_EXPORT_DIR.glob("*.txt"))
IBA_EXPORT_FILES.sort()

DATA_STEMS = [f.stem for f in IBA_EXPORT_FILES]

RAW_DATA_DIR = DATA_DIR / "raw_data"
RAW_DATA_FILES = [RAW_DATA_DIR / f"{s}.csv" for s in DATA_STEMS]

PASSES_DIR = DATA_DIR / "passes"
PASSES_FILES = [PASSES_DIR / f"{s}.csv" for s in DATA_STEMS]

PAUSES_BINS = 20
MAX_PAUSE = 15
