import pandas as pd
import pytask
from pathlib import Path
import jinja2

from weiner_variation.config import ROOT_DIR, BUILD_DIR, DATA_DIR

THIS_DIR = Path(__file__).parent
TEMPLATE = THIS_DIR / "pause_distributions.tex"
RESULT = BUILD_DIR / TEMPLATE.relative_to(ROOT_DIR)


@pytask.mark.task()
@pytask.mark.depends_on({
    "template": TEMPLATE,
    "data": DATA_DIR / "duo_pauses_dist.csv",
})
@pytask.mark.produces(RESULT)
def task_pause_distributions(depends_on: dict[..., Path], produces: Path):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE.parent))
    template = env.get_template(TEMPLATE.name)

    data = pd.read_csv(depends_on["data"], index_col=0)

    result = template.render(
        rows=[r[1] for r in data.iterrows()][:-1]
    )

    produces.write_text(result, encoding="utf-8")
