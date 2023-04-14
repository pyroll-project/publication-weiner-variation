import logging
from copy import deepcopy

import pyroll.basic as pr

from weiner_variation.config import SIM_DIR
from weiner_variation.sim.process import PASS_SEQUENCE, IN_PROFILE

logging.basicConfig(filename=SIM_DIR / "nominal.log", level=logging.INFO, filemode="w")

sequence = deepcopy(PASS_SEQUENCE)

sequence.solve(IN_PROFILE)

report = pr.report.report(sequence)

(SIM_DIR / "report.html").write_text(report, encoding="utf-8")
