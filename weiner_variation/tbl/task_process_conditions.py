import re
from copy import deepcopy

from pathlib import Path
import jinja2

from weiner_variation.config import ROOT_DIR, BUILD_DIR, SIM_DIR
from weiner_variation.sim.process import IN_PROFILE, PASS_SEQUENCE
import pyroll.core as pr

THIS_DIR = Path(__file__).parent
TEMPLATE = THIS_DIR / "process_conditions.tex"
RESULT = BUILD_DIR / TEMPLATE.relative_to(ROOT_DIR)


def format_pass_type(value: pr.RollPass):
    name = type(value.roll.groove).__name__.removesuffix("Groove")
    return re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", name).lower()


def task_process_conditions(
    template=TEMPLATE, process=SIM_DIR / "process.py", produces=RESULT
):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE.parent))
    env.filters["format_pass_type"] = format_pass_type
    template = env.get_template(TEMPLATE.name)

    sequence = deepcopy(PASS_SEQUENCE)
    sequence.solve(IN_PROFILE)

    result = template.render(
        in_profile=IN_PROFILE,
        sequence=sequence,
        roll_passes=[u for u in sequence if isinstance(u, pr.RollPass)],
        transports=[u for u in sequence if isinstance(u, pr.Transport)],
    )

    produces.write_text(result, encoding="utf-8")
