#!/bin/python3

from glob import glob
from utils import hadd, clean, get_weeks, htcondor_flag, dqm_prefix

htcondor = htcondor_flag()

# collect all histogram root files merged by run
all_files = glob(f'{dqm_prefix}/*/*/merged/*.root') #change later to dqm_prefix 
cleaned_files = clean(all_files)

# group by type (i.e. Muon, EGamma, JetMet, etc.)
file_groups = {}
for file in cleaned_files:
    parts = file.split('/')
    filename = parts[-1]
    era = parts[-3]
    label = parts[-4]
    
    target = f"{dqm_prefix}/{label}/merged/{filename}"
    if target not in file_groups:
        file_groups[target] = []
    file_groups[target].append(file)


# Hadd grouped files
for target, files in file_groups.items():
    hadd(target, files, htcondor)
    #print(target, files)
