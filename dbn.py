import pandas as pd
import re

def pad_csd(num):
    return str(num).zfill(2)

def find_lat(loc):
    coords = re.findall("\(.+\)", loc)
    lat = coords[0].split(",")[0].replace("(", "")
    return lat

def find_lon(loc):
    coords = re.findall("\(.+\)", loc)
    lon = coords[0].split(",")[1].replace(")", "").strip()
    return lon

if __name__ == '__main__': 

data = {}

data_files = ["AP_2010.csv",
    "ClassSize_201011.csv",
    "Demogra_2012.csv",
    "Grad_200510.csv",
    "Directory_201415.csv",
    "SAT_2012.csv"]

# fill dictionary with files
for f in data_files:
    d = pd.read_csv("{0}".format(f))
    key_name = f.replace(".csv", "")
    data[key_name] = d

# read in survey data for unification and filter out the significant columns from over 2000 see report:
# https://data.cityofnewyork.us/Education/2011-NYC-School-Survey/mnz3-dyi8

all_survey = pd.read_csv("masterfile11_gened_final.txt", delimiter="\t", encoding='windows-1252')
d75_survey = pd.read_csv("masterfile11_d75_final.txt", delimiter="\t", encoding='windows-1252')
survey = pd.concat([all_survey, d75_survey], axis=0)
survey["DBN"] = survey["dbn"]
survey_field = ["DBN", 
    "rr_s", 
    "rr_t", 
    "rr_p", 
    "N_s", 
    "N_t", 
    "N_p", 
    "saf_p_11", 
    "com_p_11", 
    "eng_p_11", 
    "aca_p_11", 
    "saf_t_11", 
    "com_t_11", 
    "eng_t_11", 
    "aca_t_11", 
    "saf_s_11", 
    "com_s_11", 
    "eng_s_11", 
    "aca_s_11", 
    "saf_tot_11", 
    "com_tot_11", 
    "eng_tot_11", 
    "aca_tot_11",]

survey = survey.loc[:,survey_fields]
data["survey"] = survey

# special treatment for Directory_201415 since the DBN has to be merged from "01" and "M015"
data['hs_directory']['DBN'] = data['hs_directory']['dbn']
data["class_size"]["padded_csd"] = data["class_size"]["CSD"].apply(pad_csd)
data["class_size"]["DBN"] = data["class_size"]["padded_csd"] + data["class_size"]["SCHOOL CODE"]

# totaling up SATs for analysis
cols = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
for c in cols:
    data["sat_results"][c] = pd.to_numeric(data["sat_results"][c], errors="coerce")

data['sat_results']['sat_score'] = data['sat_results'][cols[0]] + data['sat_results'][cols[1]] + data['sat_results'][cols[2]]

# extract important laction information
data["hs_directory"]["lat"] = data["hs_directory"]["Location 1"].apply(find_lat)
data["hs_directory"]["lon"] = data["hs_directory"]["Location 1"].apply(find_lon)

data["hs_directory"]["lat"] = pd.to_numeric(data["hs_directory"]["lat"], errors="coerce")
data["hs_directory"]["lon"] = pd.to_numeric(data["hs_directory"]["lon"], errors="coerce")


