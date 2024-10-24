from pathlib import Path

import jinja2

from weiner_variation.config import BUILD_DIR, ROOT_DIR
from weiner_variation.sim.process import (
    CONTACT_HEAT_TRANSFER,
    CONVECTION_HEAT_TRANSFER,
    IN_PROFILE,
    RELATIVE_RADIATION,
)

THIS_DIR = Path(__file__).parent
TEMPLATE = THIS_DIR / "material_data.tex"
RESULT = BUILD_DIR / TEMPLATE.relative_to(ROOT_DIR)


def task_material_data(template=TEMPLATE, produces=RESULT):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE.parent))
    template = env.get_template(TEMPLATE.name)

    result = template.render(
        ip=IN_PROFILE,
        c=IN_PROFILE.freiberg_flow_stress_coefficients,
        drx=IN_PROFILE.jmak_dynamic_recrystallization_parameters,
        srx=IN_PROFILE.jmak_static_recrystallization_parameters,
        mrx=IN_PROFILE.jmak_metadynamic_recrystallization_parameters,
        alpha_conv=CONVECTION_HEAT_TRANSFER,
        alpha_cont=CONTACT_HEAT_TRANSFER,
        epsr=RELATIVE_RADIATION,
    )

    produces.write_text(result, encoding="utf-8")
