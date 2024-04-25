import numpy as np

SAMPLE_COUNT = 10

FIELDS = {
    "roll_force": lambda u: getattr(u, "roll_force", np.nan),
    "roll_torque": lambda u: getattr(u.roll, "roll_torque", np.nan),
    "in_temperature": lambda u: getattr(u.in_profile, "temperature", np.nan),
    "out_temperature": lambda u: getattr(u.out_profile, "temperature", np.nan),
    "heat_turnover": lambda u: (
        u.temperature_change_by_deformation - u.temperature_change_by_contact
    )
    * u.in_profile.density
    * u.in_profile.specific_heat_capacity
    * u.volume,
    "filling_ratio": lambda u: getattr(u.out_profile, "filling_ratio", np.nan),
    "contact_area": lambda u: getattr(u, "contact_area", np.nan),
    "in_grain_size": lambda u: u.in_profile.grain_size,
    "out_grain_size": lambda u: u.out_profile.grain_size,
    "in_strain": lambda u: u.in_profile.strain,
    "out_strain": lambda u: u.out_profile.strain,
    "in_recrystallized_fraction": lambda u: u.in_profile.recrystallized_fraction,
    "out_recrystallized_fraction": lambda u: u.out_profile.recrystallized_fraction,
}

SEED = 38945729345645209345

SIMS = ["nominal", "input", "durations", "elastic"]
SIMS_STDS = ["temperature", "diameter"]
