import os, subprocess, argparse, uproot
import pandas as pd

#dqm_prefix = '/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/cmsl1dpg/www/DQM/T0PromptNanoMonit'
dqm_prefix = "/eos/user/l/lebeling/www/DQM" 
tier0 = "/eos/cms/tier0/store/data"


def run_command(cmd, log_file = "log.txt"):
    with open(log_file, "a") as f:
        subprocess.run(cmd, shell=True, stdout=f, stderr=f) 


def parse_file(fname):
        dataset = fname.split("/")[7]
        run = int("".join(fname.split("/")[11:13]))
        base_fname = fname.split("/")[-1].replace(".root","")
        era = fname.split("/")[6]
        reco_version = fname.split("/")[9]

        year = ''.join([char for char in era if char.isdigit()])
        label = ''.join([char for char in dataset if not char.isdigit()])
        
        #return f"{year}/{label}/{era}/{run}/{base_fname}"
        return f"/{label}/{era}/{dataset}/{reco_version}/{run}/{base_fname}"


def write_queue(script, infile = "", outdir = ""):
    cmd = script.replace("$INFILE", infile).replace("$OUTDIR", outdir)
    cmd = cmd.replace(" ", "___")
    with open("queue.txt", "a") as f:
        f.write(cmd + "\n")


# return weeks as dict with runnum as key -> weeks[runx] = 42
def get_weeks(year=2024):
    oms_path = f"/eos/cms/store/group/tsg/STEAM/OMSRateNtuple/{year}/physics.root"
    with uproot.open(oms_path) as f:
        df = f["tree"].arrays(
            filter_name = ['run', 'year', 'month', 'day'],
            library = "pd"
        )
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    df['week'] = df['date'].dt.isocalendar().week

    min_run = df.groupby('week')['run'].min()
    max_run = df.groupby('week')['run'].max()
    
    weeks = {}
    for _, row in df.iterrows():
        w = row['week']
        r = row['run']
        min_r = min_run[w]
        max_r = max_run[w]
        weeks[r] = f'Week{w}_{min_r}-{max_r}'

    return weeks


def hadd(target, files, htcondor = False):
    os.makedirs(os.path.dirname(target), exist_ok=True)

    # abort if merged file already exists, and it is newer than all base files
    if os.path.exists(target):
        target_time = os.path.getctime(target)
        files_time = max([os.path.getctime(file) for file in files])
        if target_time > files_time:
            print(f"skipping {target} - newer than all base files")
            return

    print(f"Hadding files with target {target}")
    cmd = f'hadd -f {target} ' + ' '.join(files)
    if htcondor: write_queue(cmd)
    else: run_command(cmd, os.path.dirname(target)+"/log.txt")


def htcondor_flag():
    parser = argparse.ArgumentParser()
    parser.add_argument('--htcondor', action='store_true', help='run on ht condor')
    args = parser.parse_args()
    if args.htcondor: os.system('rm -rf queue.txt')
    return args.htcondor


def clean(files):
    return  [file for file in files if os.path.getsize(file) >= 1600]
