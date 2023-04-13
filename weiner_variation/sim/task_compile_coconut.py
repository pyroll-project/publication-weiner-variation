import subprocess

import pytask
from pathlib import Path

THIS_DIR = Path(__file__).parent

for f in THIS_DIR.glob("*.coco"):
    @pytask.mark.task(id=f.name)
    @pytask.mark.depends_on(f)
    @pytask.mark.produces(f.with_suffix(".py"))
    def task_compile_coconut(depends_on: Path, produces: Path):
        result = subprocess.run([
            "coconut",
            "-p",
            str(depends_on),
            str(produces),
        ], capture_output=True, text=True)
        print(result.stdout)
        result.check_returncode()
