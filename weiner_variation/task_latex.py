import pytask
from pytask_latex import compilation_steps as cs

from weiner_variation.config import ROOT_FILE, RC_FILE, ROOT_DIR


@pytask.mark.latex(
    script=ROOT_FILE,
    document=ROOT_FILE.with_suffix(".pdf"),
    compilation_steps=cs.latexmk(
        options=(
            "-cd",
            "-gg",
            "-r",
            f"{RC_FILE}",
        )
    ),
)
def task_latex_compile(symbols=ROOT_DIR / "symbols.sty"):
    pass

@pytask.task
def task_cleanup_latex(pdf_file=ROOT_FILE.with_suffix(".pdf")):
    files = ROOT_DIR.glob(f"{ROOT_FILE.stem}.*")
    files_to_remove = filter(lambda f: f.suffix not in [".tex", ".pdf"], files)

    for f in files_to_remove:
        f.unlink()
