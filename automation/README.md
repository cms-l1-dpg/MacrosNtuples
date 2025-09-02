# Automation Tool Kit
Tool kit to (semi) automize production of DQM plot from NanoAODs stored on tier 0. The automation is based on the cron job scheduler which executes bash scripts and commands periodically. The following commands will be useful:

- show list of scheduled cron jobs: `acrontab -l`
- remove all scheduled cron jobs: `acrontab -r`
- open cron job editior: `acrontab -e`

last acron command:
```
0 * * * * lxplus cd /afs/cern.ch/user/l/lebeling/MacrosNtuples/automation && sh cron_job.sh >>cron.log 2>&1
```


Inside the cron jib editior:
- save changes via ctrl+o
- close editior via ctrl+x

Before running the automation tool kit, adjust the output path (i.e. the directory in which all plots and histogram are deployed) in: `utils.py` -> `dqm_prefix`

To run the automation tool kit, open the cron editor and paste the following command (replace *PATH* by the actual installation path on lxplus):
```
* */1 * * * lxplus cd /PATH/MacrosNtuples/automation && sh cron_job.sh >>cron.log 2>&1
```
Cron will execute the command once every hour saving the output messages (and errors) into the *cron.log* logfile. More details on how to configure the timing of a cron job, can be found [here](https://crontab.guru).


## automation steps
The different processing steps are summarized as: 

1) histograms
Run `python3 make_hists.py` to produce `.root` files containing histograms for all data types (i.e. EGamma, Muon, JetMet). Which selections are run is specified in `config.yaml` (see scritps). If the respective output file already exists, the histogram production is skipped. 

2) merge per run
Run `python3 merge_per_run.py` to merge (i.e. hadd) the histogram files per run. If the respective output file already exists and is newer than all base histogram files, the merging is skipped. 

3) merge per era/week
Run `python3 merge_per_era.py` to further merge (i.e. hadd) the histograms per era (i.e. Run2024H) and per week using the merged histograms per run. If the respective output file already exists and is newer than all base histogram files, the merging is skipped. 

4) merge per type
Run `python3 merge_total.py` to merge (i.e. hadd) all histograms of one data type (i.e. EGamma, Muon, JetMet) using the merged histograms per era. If the respective output file already exists and is newer than all base histogram files, the merging is skipped. 

5) plotting
Run `make_plots.py` to produce png/pdf plots from all merged histograms (merge per run/era/week/total). The plotting repective scripts are specified `condfig.yaml`. If the png/pdf files already exist and are newer than the histogram files, the plotting is skipped.  

## htcondor setup
All prduction steps listed above can be run on htcondor. Using the flag `--htcondor`, the repective plotting scripts are not directly executed but instead written into the `queue.txt` file. With `condor_submit submit.txt`, all commands in the queue are submitted to htcondor. This mode is highly recommended to (re-)run all files currently stored on tier 0. 
