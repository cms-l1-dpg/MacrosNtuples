from datetime import datetime
import ROOT
import os
import sys
import argparse



#In case you want to load an helper for C++ functions
ROOT.gInterpreter.Declare('#include "../helpers/Helper.h"')
ROOT.gInterpreter.Declare('#include "../helpers/Helper_InvariantMass.h"')
#Importing stuff from other python files
sys.path.insert(0, '../helpers')

import helper_nano_dqmoff as h


def main():
    ###Arguments 
    parser = argparse.ArgumentParser(
        description='''L1 performance studies (turnons, scale/resolution/...)
        Based on ntuples produced from MINIAOD with a code adapted from:
        https://github.com/lathomas/JetMETStudies/blob/master/JMEAnalyzer/python/JMEanalysis.py''',
        usage='use "%(prog)s --help" for more information',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--max_events", dest="max_events", help="Maximum number of events to analyze. Default=-1 i.e. run on all events.", type=int, default=-1)
    parser.add_argument("-i", "--input", dest="inputFile", help="Input file", type=str, default='')
    parser.add_argument("-o", "--output", dest="outputFile", help="Output file", type=str, default='')
    parser.add_argument("-g", "--golden", dest="golden", help="Golden JSON file to use", type = str, default = '')
    parser.add_argument("-c", "--channel", dest="channel", help=
                        '''Set channel and analysis:
                        -ZToMuMuDQMOff: For Offline DQM L1 muon studies with Z->mumu
                        -ZToEEDQMOff: For Offline DQM L1 EG studies with Z->ee
                        -ZToTauTauDQMOff: For Offline DQM L1 EG studies with Z->tautau
                        -JetsDQMOff: For Offline DQM Jet studies
                        -EtSumDQMOff: For Offline DQM EtSum studies''', 
                        type=str, default='PhotonJet')
    parser.add_argument("--config", dest="config", help="Yaml configuration file to read. Default: full config for that channel.", type=str, default='')
    #parser.add_argument("--plot_nvtx", dest="plot_nvtx", help="Whether to save additional plots in bins of nvtx. Boolean, default = False", type=bool, default=False)
    #parser.add_argument("--nvtx_bins", dest="nvtx_bins", help="Edges of the nvtx bins to use if plotNvtx is set to True. Default=[10, 20, 30, 40, 50, 60]", nargs='+', type=int, default=[10, 20, 30, 40, 50, 60])
    args = parser.parse_args() 

    ###Define the RDataFrame from the input tree
    inputFile = args.inputFile
    if inputFile == '':
        if args.channel == 'ZToEEDQMOff':
            inputFile = '/pnfs/iihe/cms/ph/sc4/store/data/Run2023C/EGamma0/NANOAOD/PromptNanoAODv11p9_v1-v1/70000/3b1e99a5-71a0-46ee-b720-b79669f60029.root'
        elif args.channel == 'ZToMuMuDQMOff':
            inputFile = '/pnfs/iihe/cms/ph/sc4/store/data/Run2023C/Muon1/NANOAOD/PromptNanoAODv12_v2-v2/60000/ee7372a9-da2d-4b3e-8a0e-3cba6d2272a5.root'
        elif args.channel == 'ZToTauTauDQMOff':
            inputFile = '/pnfs/iihe/cms/ph/sc4/store/data/Run2023C/Muon1/NANOAOD/PromptNanoAODv12_v2-v2/60000/ee7372a9-da2d-4b3e-8a0e-3cba6d2272a5.root'
        elif args.channel == 'JetsDQMOff':
            inputFile = '/pnfs/iihe/cms/ph/sc4/store/data/Run2023C/Muon1/NANOAOD/PromptNanoAODv12_v2-v2/60000/ee7372a9-da2d-4b3e-8a0e-3cba6d2272a5.root'
        elif args.channel == 'EtSumDQMOff' :
            inputFile = '/pnfs/iihe/cms/ph/sc4/store/data/Run2023C/Muon1/NANOAOD/PromptNanoAODv12_v2-v2/60000/ee7372a9-da2d-4b3e-8a0e-3cba6d2272a5.root'

    ### Set default config file
    config_file = args.config
    if config_file == '':
        if args.channel == 'ZToMuMuDQMOff':
            config_file = '../config_cards/full_ZToMuMu_DQMOff.yaml'
        elif args.channel == 'ZToEEDQMOff':
            config_file = '../config_cards/full_ZToEE_DQMOff.yaml'
        elif args.channel == 'ZToTauTauDQMOff':
            config_file = '../config_cards/full_ZToTauTau_DQMOff.yaml'
        elif args.channel == 'JetsDQMOff':
            config_file = '../config_cards/full_Jet_DQMOff.yaml'
        elif args.channel == 'EtSumDQMOff':
            config_file = '../config_cards/full_EtSum_DQMOff.yaml'

    # Read config and set config_dict in helper
    with open(config_file) as s:
        h.set_config(s)

    fltr = h.make_filter(args.golden)

    ### Create filters and suffix, if needed, to later run on bins of nvtx

    filter_list = ["true"]
    suffix_list = [""]

    # bins of nvtx
    #if args.plot_nvtx == True:
    if h.config['PU_plots']['make_histos']:
        filter_list += ["PV_npvs>={}&&PV_npvs<{}".format(low, high) for (low, high) \
                in zip(h.config['PU_plots']['nvtx_bins'][:-1],h.config['PU_plots']['nvtx_bins'][1:])]
        suffix_list += ["_nvtx{}to{}".format(low, high) for (low, high) \
                in zip(h.config['PU_plots']['nvtx_bins'][:-1],h.config['PU_plots']['nvtx_bins'][1:])]

    ###

    df = ROOT.RDataFrame('Events', inputFile)

    if fltr != '':
        df = df.Filter(fltr)
    nEvents = df.Count().GetValue()

    print('There are {} events'.format(nEvents))

    if nEvents == 0:
        print('No events, exiting.')
        exit()

    max_events = min(nEvents, args.max_events) if args.max_events >=0 else nEvents
    df = df.Range(0, max_events)

    #Next line to monitor event loop progress
    df = df.Filter('if(tdfentry_ %100000 == 0) {cout << "Event is  " << tdfentry_ << endl;} return true;')

    #Apply MET filters
    df = df.Filter('Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_goodVertices&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&Flag_BadPFMuonDzFilter')

    # binning for run number
    h.set_runnb_bins(df)
    
    if args.outputFile == '':
        args.outputFile = 'output_'+args.channel+'.root'
    out = ROOT.TFile(args.outputFile, "recreate")
    ####The sequence of filters/column definition starts here
    
    if args.channel not in ['ZToMuMuDQMOff','ZToEEDQMOff','ZToTauTauDQMOff', 'JetsDQMOff', 'EtSumDQMOff']:
        print("Channel {} does not exist".format(args.channel))
        return 

    # add nvtx histo
    nvtx_histo = df.Histo1D(ROOT.RDF.TH1DModel("h_nvtx" , "Number of reco vertices;N_{vtx};Events"  ,    100, 0., 100.), "PV_npvs")
    nvtx_histo.GetValue().Write()
        
    # Define PF JetID
    df = h.PassPFJetID(df)

    if args.channel == 'ZToEEDQMOff':

        print('Electron DQM Offline Hist production')
        print('---------------------------------')
        df = h.DQMOff_EleSelection(df)

        all_histos = {}        
        df, histos = h.ZEE_DQMOff_Plots(df, suffix = '')
        for key, val in histos.items():
            all_histos[key] = val

        for i in all_histos:
            all_histos[i].GetValue().Write()

    if args.channel == 'ZToMuMuDQMOff':

        print('Muon DQM Offline Hist production')
        print('---------------------------------')
        df = h.DQMOff_MuSelection(df)

        all_histos = {}        
        df, histos = h.ZMuMu_DQMOff_Plots(df, suffix = '')
        for key, val in histos.items():
            all_histos[key] = val

        for i in all_histos:
            all_histos[i].GetValue().Write()

    if args.channel == 'ZToTauTauDQMOff':

        print('Tau DQM Offline Hist production')
        print('---------------------------------')

        df = h.DQMOff_TauSelection(df)

        all_histos = {}
        df, histos = h.ZTauTau_DQMOff_Plots(df, suffix = '')
        df_rep = df.Report()
        df_rep.Print()
        for key, val in histos.items():
            all_histos[key] = val

        for i in all_histos:
            all_histos[i].GetValue().Write()

        
    if args.channel == 'JetsDQMOff':

        print('Jet DQM Offline Hist production')
        print('---------------------------------')
        df = h.DQMOff_JetSelection(df)

        all_histos = {}
        df, histos = h.Jet_DQMOff_Plots(df, suffix = '')
        for key, val in histos.items():
            all_histos[key] = val

        for i in all_histos:
            all_histos[i].GetValue().Write()

    if args.channel == 'EtSumDQMOff':

        print('EtSum DQM Offline Hist production')
        print('---------------------------------')
        df = h.DQMOff_EtSumSelection(df)

        all_histos = {}
        df, histos = h.EtSum_DQMOff_Plots(df, suffix = '')
        for key, val in histos.items():
            all_histos[key] = val

        for i in all_histos:
            all_histos[i].GetValue().Write()

if __name__ == '__main__':
    main()
