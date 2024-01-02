import pyroll.core as pr
from pyroll.freiberg_flow_stress import FreibergFlowStressCoefficients

REVERSING_PAUSE_DURATION = 6
LAST_REVERSING_PAUSE_DURATION = 9


def create_in_profile(diameter, temperature):
    return pr.Profile.round(
        diameter=diameter,
        temperature=temperature,
        density=7.5e3,
        specific_heat_capacity=690,
        material="C45",
        strain=0,
        freiberg_flow_stress_coefficients=FreibergFlowStressCoefficients(
            a=2731.39 * 1e6,
            m1=-0.00268,
            m2=0.31076,
            m3=0,
            m4=-0.00056,
            m5=0.00046,
            m6=0,
            m7=-0.98375,
            m8=0.000139,
            m9=0,
            baseStrain=0.1,
            baseStrainRate=0.1
        ),
    )


DIAMETER = 50e-3
TEMPERATURE = 1150 + 273.15
IN_PROFILE = create_in_profile(DIAMETER, TEMPERATURE)

DIAMETER_STD = 1e-3
TEMPERATURE_STD = 10

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
        duration=LAST_REVERSING_PAUSE_DURATION
    ),
    pr.RollPass(
        label="F1",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=2.5e-3,
                usable_width=15.6e-3,
                depth=(8.1e-3 - 2.3e-3) / 2,
            ),
            nominal_radius=107.5e-3,
        ),
        velocity=7.9,
        gap=2.3e-3,
    ),
    pr.Transport(
        duration=1.5 / 7.9
    ),
    pr.RollPass(
        label="F2",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=0.5e-3,
                r2=5.1e-3,
                depth=(10e-3 - 1.5e-3) / 2
            ),
            nominal_radius=107.5e-3,
        ),
        velocity=9.3,
        gap=1.5e-3,
    ),
    pr.Transport(
        duration=1.5 / 9.3
    ),
    pr.RollPass(
        label="F3",
        roll=pr.Roll(
            groove=pr.CircularOvalGroove(
                r1=2.5e-3,
                usable_width=12.8e-3,
                depth=(6.2e-3 - 1.96e-3) / 2,
            ),
            nominal_radius=107.5e-3,
        ),
        velocity=12.06,
        gap=1.96e-3,
    ),
    pr.Transport(
        duration=1.5 / 12.06
    ),
    pr.RollPass(
        label="F4",
        roll=pr.Roll(
            groove=pr.RoundGroove(
                r1=0.5e-3,
                r2=4.1e-3,
                depth=(8e-3 - 1.5e-3) / 2
            ),
            nominal_radius=85e-3,
        ),
        velocity=15.75,
        gap=1.5e-3,
    ),
])

CONTACT_HEAT_TRANSFER = 5000
CONVECTION_HEAT_TRANSFER = 10
RELATIVE_RADIATION = 0.8
ROLL_TEMPERATURE = 293.15

for u in PASS_SEQUENCE:
    if isinstance(u, pr.RollPass):
        u.roll.contact_heat_transfer_coefficient = CONTACT_HEAT_TRANSFER
        u.roll.elastic_modulus = 210e9
        u.roll.poissons_ratio = 0.3
        u.roll.temperature = ROLL_TEMPERATURE
    if isinstance(u, pr.Transport):
        u.convection_heat_transfer_coefficient = CONVECTION_HEAT_TRANSFER
        u.relative_radiation_coefficient = RELATIVE_RADIATION
