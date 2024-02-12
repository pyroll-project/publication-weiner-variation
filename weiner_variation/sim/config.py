import numpy as np

SAMPLE_COUNT = 1000

FIELDS = {
    "roll_force": lambda u: getattr(u, "roll_force", np.nan),
    "roll_torque": lambda u: getattr(u.roll, "roll_torque", np.nan),
    "in_temperature": lambda u: getattr(u.in_profile, "temperature", np.nan),
    "out_temperature": lambda u: getattr(u.out_profile, "temperature", np.nan),
    "filling_ratio": lambda u: getattr(u.out_profile, "filling_ratio", np.nan),
    "contact_area": lambda u: getattr(u, "contact_area", np.nan),
    "strain": lambda u: getattr(u, "strain", np.nan),
}

SEED = 38945729345645209345
