import os
import pandas as pd

dir = "C:/Users/Jeffrey/GitHub/road_upgrades/python_road_upgrades/Exports/Points/composites_2"
files = os.listdir(dir)

for f in files:
    fp = f"{dir}/{f}"
    df = pd.read_csv(fp)
    print(df.columns)
    df['coords'] = ""
    df = df.iloc[0:1000, :]
    df.to_csv(fp)