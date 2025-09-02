#!/bin/python3

import os, sys, time, subprocess
from glob import glob

path_prefix = "/eos/cms/tier0/store/data"

config_dict = {
    "JetMET" : # for JetMET plots
        {
            "datasets" : ["JetMET0","JetMET1"],
            "eras" : ["Run2024*"],
            "scripts": [
                "python3 performances_nano.py -i $INFILE -o $OUTDIR/all_DiJet.root -c DiJet",  
                "python3 ../plotting/make_DiJet_plots.py --dir $OUTDIR --config ../config_cards/full_DiJet.yaml",
                ]
        },
    "EGamma" : # for JetMET plots
        {
            "datasets" : ["EGamma0","EGamma1"],
            "eras" : ["Run2024*"],
            "scripts": [
                "python3 performances_nano.py -i $INFILE -o $OUTDIR/all_PhotonJet.root -c PhotonJet",
                "python3 performances_nano.py -i $INFILE -o $OUTDIR/all_ZToEE.root -c ZToEE",

                ## OFF DQM
                "python3 performances_nano_dqmoff.py -i $INFILE -o $OUTDIR/oug_zee_dqmoff.root -c ZToEEDQMOff",
                ## Plot
                "python3 ../plotting/make_ZToEE_plots.py --dir $OUTDIR --config ../config_cards/full_ZToEE.yaml",
                "python3 ../plotting/make_PhotonJet_plots.py --dir $OUTDIR --config ../config_cards/full_PhotonJet.yaml",
            ]
        },
    "Muon" : # for JetMET plots
        {
            "datasets" : ["Muon0","Muon1"],
            "eras" : ["Run2024*"],            
            "scripts" : [
                "/bin/python3 performances_nano.py -i $INFILE -o $OUTDIR/all_ZToMuMu.root -c ZToMuMu",
                "/bin/python3 performances_nano.py -i $INFILE -o $OUTDIR/all_MuonJet.root -c MuonJet",
                "/bin/python3 performances_nano.py -i $INFILE -o $OUTDIR/all_ZToTauTau.root -c ZToTauTau ",
                ## OFF DQM
                "/bin/python3 performances_nano_dqmoff.py -i $INFILE -o $OUTDIR/out_zmumu_dqmoffl.root -c ZToMuMuDQMOff",
                "/bin/python3 performances_nano_dqmoff.py -i $INFILE -o $OUTDIR/out_jets_dqmoff.root -c JetsDQMOff ",
                "/bin/python3 performances_nano_dqmoff.py -i $INFILE -o $OUTDIR/out_ztautau_dqmoff.root -c ZToTauTauDQMOff",
                "/bin/python3 performances_nano_dqmoff.py -i $INFILE -o $OUTDIR/out_zmumu_dqmoffl.root -c ZToMuMuDQMOff",
                "/bin/python3 performances_nano_dqmoff.py -i $INFILE -o $OUTDIR/out_etsum_dqmoff.root -c EtSumDQMOff",
                ## plotting
                "/bin/python3 ../plotting/make_ZToMuMu_plots.py --dir $OUTDIR --config ../config_cards/full_ZToMuMu.yaml",
                "/bin/python3 ../plotting/make_ZToTauTau_plots.py --dir $OUTDIR --config ../config_cards/full_ZToTauTau.yaml",
                "/bin/python3 ../plotting/make_MuonJet_plots.py --dir $OUTDIR --config ../config_cards/full_MuonJet.yaml",
                ]
        }
}


import random

for label, config in config_dict.items():
    print(80*"#")
    print(80*"#")
    print(f"  Running plots for {label}")
    print(80*"#")

    fnames = []
    for dataset in config["datasets"]:
        for era in config["eras"]:
            fnames += glob(f"{path_prefix}/{era}/{dataset}/NANOAOD/PromptReco-v*/*/*/*/*/*.root")

    #print(fnames)
    if len(fnames) > 0:
        # do random choice for now
        fname = random.choice(fnames)

        ## take the latest file from T0 eos 
        #fname = fnames[-1]
    else:
        continue

    ## decode file path to run, era etc
    fname_split = fname.split("/")    
    dataset = fname.split("/")[7]
    run = int("".join(fname.split("/")[11:13]))
    base_fname = fname.split("/")[-1].replace(".root","")
    era = fname.split("/")[6]
    reco_version = fname.split("/")[9]

    outdir = f"{era}/{dataset}/{reco_version}/{run}/{base_fname}"

    # check output exists
    #out_web_path = "/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/cmsl1dpg/www/DQM/T0PromptNanoMonit/"  + outdir
    out_web_path = "/eos/home-l/lebeling/www/DQM/" + outdir 

    if os.path.exists(out_web_path):
        # out_web_path + "_1"
        print("Output already exists!")
        print(out_web_path)
        continue
    else:
        os.makedirs(out_web_path)
        os.makedirs(out_web_path+"/plotsL1Run3") # for plots
    ### Main part: run the performance code

    #script_dir = "/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/cmsl1dpg/MacrosNtuples/l1macros"
    script_dir = "/eos/home-l/lebeling/projects/MacrosNtuples/l1macros"
    os.chdir(script_dir)

    for script in config["scripts"]:
        print(80*"#")
        print(80*"#")
        print(script)
        print(80*"#")

        script = script.replace("$INFILE",fname).replace("$OUTDIR",out_web_path)

        print(f"Going to process {fname} and store output here: {out_web_path}")
        #ret = subprocess.run([script_path, out_web_path, fname, ">> logs"],)
        # print(script.split(" "))
        if "/" in script.split(" ")[-1]:
            log_fname = out_web_path + "/" + os.path.basename(script.split(" ")[-1])+".log"
        else:
            log_fname = out_web_path + "/" + script.split(" ")[-1]+".log"
        print(f"Writing logs to {log_fname}")
        with open(log_fname, "w") as f:
            ret = subprocess.run(
                #script.split(" "), 
                script,
                shell = True, 
                stdout=f, 
                stderr=f
                )

    ### Hadd the outputs of a full run?
    # break
