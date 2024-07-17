import subprocess
from pathlib import Path

import pytask

THIS_DIR = Path(__file__).parent

for f in THIS_DIR.glob("*.coco"):

    @pytask.task(id=f.name)
    def task_compile_coconut(coconut_file=f, python_file=f.with_suffix(".py")):
        result = subprocess.run(
            [
                "coconut",
                "-p",
                str(coconut_file),
                str(python_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout)
        result.check_returncode()
