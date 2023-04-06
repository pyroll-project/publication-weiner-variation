import pytask as pytask
from pytask_latex import compilation_steps as cs

from weiner_variation.config import ROOT_FILE, RC_FILE, ROOT_DIR


@pytask.mark.latex(
    script=ROOT_FILE,
    document=ROOT_FILE.with_suffix(".pdf"),
    compilation_steps=cs.latexmk(
        options=("-r", f"{RC_FILE}",)
    ),
)
def task_latex_compile():
    pass


@pytask.mark.depends_on(ROOT_FILE.with_suffix(".pdf"))
def task_cleanup_latex():
    files = ROOT_DIR.glob(f"{ROOT_FILE.stem}.*")
    files_to_remove = filter(lambda f: f.suffix not in [".tex", ".pdf"], files)

    for f in files_to_remove:
        f.unlink()
