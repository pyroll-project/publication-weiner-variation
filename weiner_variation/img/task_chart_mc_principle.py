import pytask as pytask
from schemdraw import Drawing
from schemdraw.elements import DotDotDot, ElementCompound, EncircleBox
from schemdraw.flow import Arrow, Box, Data, Subroutine, Wire

from weiner_variation.config import IMG_DIR

RUN_DISTANCE = 3.5


class Run(ElementCompound):
    def __init__(self, i, *d, **kwargs):
        super().__init__(*d, **kwargs)
        self.right()
        self.add(d_in := Data().label("random\ninput state"))
        self.add(Arrow().length(1))
        self.add(Subroutine().label("simulation"))
        self.add(Arrow().length(1))
        self.add(d_out := Data().label("result data"))

        self.add(EncircleBox([d_in, d_out]).linewidth(1).linestyle("--").label(f"Run \\#{i}"))

        self.anchors = {
            "start": d_in.W,
            "end": d_out.E,
            "center": (d_in.W + d_out.E) / 2,
        }

        self.anchor("start")


def task_flow_chart_mc_principle(produces=[IMG_DIR / f"chart_mc_principle.{s}" for s in ["svg", "pdf", "png"]]):
    with Drawing() as d:
        d.add(b_sample := Box().label("random\nsampling"))

        d.add(r1 := Run(1).at(b_sample.E, d.unit, RUN_DISTANCE))
        d.add(r2 := Run(2).at(b_sample.E, d.unit, 0))
        d.add(DotDotDot().at(r2.center, 0, -0.675 * RUN_DISTANCE + 1).down())
        d.add(rn := Run("n").at(b_sample.E, d.unit, -1.5 * RUN_DISTANCE))

        d.add(Wire("z", arrow="->").at(b_sample.E).to(r1.start))
        d.add(Wire("z", arrow="->").at(b_sample.E).to(r2.start))
        d.add(Wire("z", arrow="->").at(b_sample.E).to(rn.start))

        d.add(b_coll := Box().label("collection\n+\nanalysis").at(r2.end, d.unit))

        d.add(Wire("z", arrow="->").at(r1.end).to(b_coll.W))
        d.add(Wire("z", arrow="->").at(r2.end).to(b_coll.W))
        d.add(Wire("z", arrow="->").at(rn.end).to(b_coll.W))

        d.add(
            Data(w=5.5)
            .label("statistically distributed\ninput data")
            .at((b_sample.N.x, r1.start.y), -0.5)
            .anchor("center")
            .drop("S")
        )
        d.add(Arrow().to(b_sample.N))

        d.add(
            Data(w=5.5)
            .label("statistically distributed\nresult data")
            .at((b_coll.N.x, r1.end.y), 0.5)
            .anchor("center")
            .drop("S")
        )
        d.add(Arrow().to(b_coll.N).reverse())

        # d.draw().getfig().set_constrained_layout(True)

        for p in produces:
            d.save(str(p))
