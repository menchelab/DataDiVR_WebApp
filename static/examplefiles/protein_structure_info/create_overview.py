import pandas as pd
import os

WD = os.path.dirname(os.path.abspath(__file__))
os.chdir(WD)

cartoon = pd.read_csv("./scales_Cartoon.csv")
cartoon = cartoon.drop_duplicates(subset=["UniProtID"])
cartoon = cartoon.set_index("UniProtID")

electrostatic = pd.read_csv("./scales_electrostatic_surface.csv")
electrostatic = electrostatic.drop_duplicates(subset=["UniProtID"])
electrostatic = electrostatic.set_index("UniProtID")

overview = pd.DataFrame(
    columns=[
        "pdb_file",
        "multi_structure",
        "parts",
        "cartoons_ss_coloring",
    ],
    index=cartoon.index,
)

overview.loc[cartoon.index, "cartoons_ss_coloring"] = cartoon["scale"]
overview["cartoons_ss_coloring"] = cartoon["scale"]
overview.loc[electrostatic.index, "electrostatic_surface"] = electrostatic["scale"]
overview.to_csv("./overview.csv")
