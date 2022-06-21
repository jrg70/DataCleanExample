import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

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

def first_char(dbn):
    return dbn[0:2]

if __name__ == '__main__': 

## Cleaning the data and merge it together
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

# condense datasets for unique dbn
# 1. class size: filter, group, aggregate, reindex and assign back to data
data["class_size"] = data["class_size"][data["class_size"]["GRADE "] == "09-12"]
data["class_size"] = data["class_size"][data["class_size"]["PROGRAM TYPE"] == "GEN ED"]
data["class_size"] = data["class_size"].groupby('DBN').agg(np.mean)
data["class_size"].reset_index(inplace = True)

# 2. Demographics: filter
data['demographics'] = data['demographics'][data['demographics']['schoolyear'] == 20112012]

# 3. Graduation
data["graduation"] = data["graduation"][data["graduation"]["Cohort"] == "2006"]
data["graduation"] = data["graduation"][data["graduation"]["Demographic"] == "Total Cohort"]

# convert to numeric values
cols = ['AP Test Takers ', 'Total Exams Taken', 'Number of Exams with scores 3 4 or 5']
for col in cols:
    data["ap_2010"][col] = pd.to_numeric(data["ap_2010"][col], errors="coerce")
    
# MERGE data
# Stragtegy: left  to preserve most SAT results
combined = data["sat_results"]

to_merge = ["ap_2010","graduation"]
for m in to_merge:
    combined = combined.mege(data[m], on='DBN', how='left')

to_merge = ["class_size", "demographics", "survey", "hs_directory"]
for m in to_merge:
    combined = combined.merge(data[m], on="DBN", how="inner")
    
print(combined.shape, combined.head(5))

# (imputation) fill Nans with mean and for columns with mean Nan 0
combined = combined.fillna(combined.mean())
combined = combined.fillna(0)

# Analysation aid
combined['school_dist'] = combined['DBN'].apply(reduce)

## Analysis
# Check correlations
correlations = combined.corr()["sat_score"]
print(correlations)

# visualise example
combined.plot.scatter(x='total_enrollment', y='sat_score')
plt.show()
