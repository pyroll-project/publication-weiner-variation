import pytask
from pathlib import Path
import jinja2

from weiner_variation.config import BUILD_DIR, ROOT_DIR
from weiner_variation.sim.process import IN_PROFILE, CONVECTION_HEAT_TRANSFER, CONTACT_HEAT_TRANSFER, RELATIVE_RADIATION

THIS_DIR = Path(__file__).parent
TEMPLATE = THIS_DIR / "material_data.tex"
RESULT = BUILD_DIR / TEMPLATE.relative_to(ROOT_DIR)


@pytask.mark.task()
@pytask.mark.depends_on({
    "template": TEMPLATE,
})
@pytask.mark.produces(RESULT)
def task_material_data(depends_on: Path, produces: Path):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE.parent))
    template = env.get_template(TEMPLATE.name)

    result = template.render(
        ip=IN_PROFILE,
        c=IN_PROFILE.freiberg_flow_stress_coefficients,
        alpha_conv=CONVECTION_HEAT_TRANSFER,
        alpha_cont=CONTACT_HEAT_TRANSFER,
        epsr=RELATIVE_RADIATION,
    )

    produces.write_text(result, encoding="utf-8")
