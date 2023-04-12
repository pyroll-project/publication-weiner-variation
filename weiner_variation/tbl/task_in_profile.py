import pytask
from pathlib import Path
import jinja2

from weiner_variation.config import BUILD_DIR, ROOT_DIR, SIM_DIR
from weiner_variation.sim.process import IN_PROFILE

THIS_DIR = Path(__file__).parent
TEMPLATE = THIS_DIR / "in_profile.tex"
RESULT = BUILD_DIR / TEMPLATE.relative_to(ROOT_DIR)


@pytask.mark.task()
@pytask.mark.depends_on({
    "template": TEMPLATE,
    "process": SIM_DIR / "process.py"
})
@pytask.mark.produces(RESULT)
def task_in_profile(depends_on: Path, produces: Path):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE.parent))
    template = env.get_template(TEMPLATE.name)

    result = template.render(
        in_profile=IN_PROFILE,
    )

    produces.write_text(result, encoding="utf-8")
