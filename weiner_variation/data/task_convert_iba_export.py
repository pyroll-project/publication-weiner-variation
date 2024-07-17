import pandas as pd
import pytask

from weiner_variation.data.config import IBA_EXPORT_FILES, MATERIALS, RAW_DATA_FILES

for material in MATERIALS:
    for iba_file, export_file in zip(IBA_EXPORT_FILES[material], RAW_DATA_FILES[material], strict=False):

        @pytask.task(id=f"{material}/{iba_file.stem}")
        def task_convert_iba_export(in_file=iba_file, produces=export_file):
            df_in = pd.read_csv(in_file, header=0, index_col=0, skiprows=[0, 2], encoding="iso-8859-15")

            df_out = pd.DataFrame(
                {
                    "roll_force_duo": df_in["Walzkraft  DUO-Walzwerk VL"]
                    + df_in["Walzkraft  DUO-Walzwerk VR"]
                    + df_in["Walzkraft  DUO-Walzwerk HL"]
                    + df_in["Walzkraft  DUO-Walzwerk HR"],
                    "roll_force_f1": df_in["Walzkraft Walzgerüst 1"],
                    "roll_force_f2": df_in["Walzkraft Walzgerüst 2"],
                    "roll_force_f3": df_in["Walzkraft Walzgerüst 3"],
                    "roll_force_f4": df_in["Walzkraft Walzgerüst 4"],
                    "roll_torque_duo": df_in["Moment DUO-Walzwerk"],
                    "roll_torque_f1": df_in["Moment Walzgerüst 1"],
                    "roll_torque_f2": df_in["Moment Walzgerüst 2"],
                    "roll_torque_f3": df_in["Moment Walzgerüst 3"],
                    "roll_torque_f4": df_in["Moment Walzgerüst 4"],
                    "temp_1": df_in["Temperatur 1 (Rollgang)"],
                    "temp_2": df_in["Temperatur 2 (Duo Austritt)"],
                    "temp_3": df_in["Temperatur 3 (Duo Anstich)"],
                    "temp_4": df_in["Temperatur 4 (vor G1)"],
                    "temp_5": df_in["Temperatur 5 (vor G2)"],
                    "temp_6": df_in["Temperatur 6 (vor G3)"],
                    "temp_7": df_in["Temperatur 7 (vor G4)"],
                    "temp_8": df_in["Temperatur 8 (nach G4)"],
                }
            )

            df_out.to_csv(produces)
