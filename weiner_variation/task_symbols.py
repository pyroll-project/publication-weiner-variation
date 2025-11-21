import tomli
import pytask
import re

from weiner_variation.config import ROOT_DIR

RE_ARGUMENT = re.compile(r"#\d")


def create_command_def(name: str, code: str):
    if "#" in code:
        arguments = RE_ARGUMENT.findall(code)
        return rf"\gdef\{name}{''.join(arguments)}{{{code}}}"
    else:
        return rf"\gdef\{name}{{{code}}}"


@pytask.task()
def task_symbols(
    symbols_toml=ROOT_DIR / "symbols.toml", produces=ROOT_DIR / "symbols.sty"
):
    input_text = symbols_toml.read_text()
    input_lines = input_text.splitlines()
    symbols_toml.write_text("\n".join(sorted(input_lines)))

    data = tomli.loads(input_text)

    lines = [create_command_def(n, c) for n, c in data.items()]

    produces.write_text("\n".join(lines))
