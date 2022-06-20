import pandas as pd

data = {}

data_files = ["AP_2010.csv",
    "ClassSize_201011.csv",
    "Demogra_2012.csv",
    "Grad_200510.csv",
    "Directory_201415.csv",
    "SAT_2012.csv"]

for f in data_files:
    d = pd.read_csv("{0}".format(f))
    key_name = f.replace(".csv", "")
    data[key_name] = d
