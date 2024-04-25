import pytask
from pathlib import Path
import jinja2

from weiner_variation.config import BUILD_DIR, ROOT_DIR, SIM_DIR
from weiner_variation.sim.process import IN_PROFILE

THIS_DIR = Path(__file__).parent
TEMPLATE = THIS_DIR / "flow_stress.tex"
RESULT = BUILD_DIR / TEMPLATE.relative_to(ROOT_DIR)


def task_flow_stress(
    template=TEMPLATE, process=SIM_DIR / "process.py", produces=RESULT
):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE.parent))
    template = env.get_template(TEMPLATE.name)

    result = template.render(c=IN_PROFILE.freiberg_flow_stress_coefficients)

    produces.write_text(result, encoding="utf-8")
