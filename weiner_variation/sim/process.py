import pyroll.core as pr
from pyroll.freiberg_flow_stress import FreibergFlowStressCoefficients

REVERSING_PAUSE_DURATION = 6.1


def create_in_profile(diameter, temperature):
    return pr.Profile.round(
        diameter=diameter,
        temperature=temperature,
        density=7.5e3,
        thermal_capacity=690,
        material="BST 500",
        strain=0,
        freiberg_flow_stress_coefficients=FreibergFlowStressCoefficients(
            a=4877.12 * 1e6,
            m1=-0.00273339,
            m2=0.302309,
            m3=-0.0407581,
            m4=0.000222222,
            m5=-0.000383134,
            m6=0,
            m7=-0.492672,
            m8=0.0000175044,
            m9=-0.0611783,
            baseStrain=0.1,
            baseStrainRate=0.1
        ),
    )


DIAMETER = 50e-3
TEMPERATURE = 1100 + 273.15
IN_PROFILE = create_in_profile(DIAMETER, TEMPERATURE)

PASS_SEQUENCE = pr.PassSequence([
    pr.RollPass(
        label="R1",
        roll=pr.Roll(
            groove=pr.SwedishOvalGroove(
                r1=6e-3,
                r2=26e-3,
                ground_width=38e-3,
                usable_width=60e-3,
                depth=7.25e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=1,
        gap=13.5e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R2",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=4e-3,
                r2=18e-3,
                depth=17.5e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=1,
        gap=1.5e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R3",
        roll=pr.Roll(
            groove=pr.SwedishOvalGroove(
                r1=6e-3,
                r2=26e-3,
                ground_width=38e-3,
                usable_width=60e-3,
                depth=7.25e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=1.5e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R4",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=4e-3,
                r2=13.5e-3,
                depth=12.5e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=1e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R5",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=6e-3,
                r2=38e-3,
                depth=4e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=5.4e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R6",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=3e-3,
                r2=10e-3,
                depth=9e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=1.8e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R7",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=6e-3,
                r2=38e-3,
                depth=4e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=0.8e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R8",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=2e-3,
                r2=7.5e-3,
                depth=5.5e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=3.8e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="R9",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=6e-3,
                r2=21.2e-3,
                depth=2.5e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=3.5e-3,
    ),
    pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ), pr.RollPass(
        label="R10",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=0.5e-3,
                r2=6e-3,
                depth=4e-3
            ),
            nominal_radius=321e-3 / 2,
        ),
        velocity=2,
        gap=4e-3,
    ), pr.Transport(
        duration=REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="F1",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=2.5e-3,
                r2=12.5e-3,
                depth=2.9e-3
            ),
            nominal_radius=107.5e-3,
        ),
        velocity=4.89,
        gap=2.3e-3,
    ),
    pr.Transport(
        duration=1.5 / 4.89
    ),
    pr.RollPass(
        label="F2",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=0.5e-3,
                r2=5.1e-3,
                depth=4.25e-3
            ),
            nominal_radius=107.5e-3,
        ),
        velocity=6.1,
        gap=1.5e-3,
    ),
    pr.Transport(
        duration=1.5 / 6.1
    ),
    pr.RollPass(
        label="F3",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=2.5e-3,
                r2=11e-3,
                depth=2.12e-3
            ),
            nominal_radius=107.5e-3,
        ),
        velocity=7.91,
        gap=1.9e-3,
    ),
    pr.Transport(
        duration=1.5 / 7.91
    ),
    pr.RollPass(
        label="F4",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=0.5e-3,
                r2=4.0e-3,
                depth=3.7e-3
            ),
            nominal_radius=85e-3,
        ),
        velocity=10,
        gap=1.5e-3,
    ),
])

for u in PASS_SEQUENCE:
    if isinstance(u, pr.RollPass):
        u.roll.contact_heat_transfer_coefficient = 5000
        u.roll.elastic_modulus = 210e9
        u.roll.poissons_ratio = 0.3
        u.roll.temperature = 293.15
    if isinstance(u, pr.Transport):
        u.convection_heat_transfer_coefficient = 10
        u.relative_radiation_coefficient = 0.8
