import os
from pathlib import Path

import pytask
import tomli

from weiner_variation.config import ROOT_DIR


def create_command_def(name: str, code: str):
    if "#" in code:
        par_count = code.count("#")
        return rf"\newcommand{{\{name}}}[{par_count}]{{{{{code}}}}}"
    else:
        return rf"\newcommand{{\{name}}}{{{{{code}}}}}"


def task_symbols(
    depends_on=ROOT_DIR / "symbols.toml", produces=ROOT_DIR / "symbols.sty"
):
    input_text = depends_on.read_text()
    input_lines = input_text.splitlines()
    depends_on.write_text("\n".join(sorted(input_lines)))

    data = tomli.loads(input_text)

    lines = [create_command_def(n, c) for n, c in data.items()]

    produces.write_text("\n".join(lines))
