# make_ZToEE_plots.py, a program to draw the L1Studies plots obtained from the histograms extracted from NanoAOD
eventselection='Z#rightarrow ee'
subfolder='/plots_ztoee'
channelname='ZToEE'

import yaml
import drawplots
import argparse
import os

def main():
    parser = argparse.ArgumentParser(
        description='''Plotter''',
        usage='use "%(prog)s --help" for more information',
        formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("-d", "--dir", dest="dir", help="The directory to read the inputs files from and draw the plots to", type=str, default='./')
    parser.add_argument("-c", "--config", dest="config", help="The YAML config to read from", type=str, default='../config_cards/full_ZToEE.yaml')
    parser.add_argument("-l", "--lumi", dest="lumi", help="The integrated luminosity to display in the top right corner of the plot", type=str, default='')

    args = parser.parse_args()
    config = yaml.safe_load(open(args.config, 'r'))

    input_file = args.dir + "/all_ZToEE.root"
    if args.lumi != '':
        toplabel="#sqrt{s} = 13.6 TeV, L_{int} = " + args.lumi #+ " fb^{-1}"
    else:
        toplabel="#sqrt{s} = 13.6 TeV"

    suffixes = ['']
    if config['PU_plots']['make_histos']:
        bins = config['PU_plots']['nvtx_bins']
        suffixes += ['_nvtx{}to{}'.format(bins[i], bins[i+1]) for i in range(len(bins) - 1)]

    os.makedirs(args.dir + subfolder, exist_ok=True)

    # NVTX distribution:
    drawplots.makedist(
            inputFiles_list = [input_file],
            saveplot = True,
            h1d = ['h_nvtx'],
            xtitle = 'N_{vtx}',
            ytitle = 'Events',
            top_label = toplabel,
            plotname = channelname + '_L1EG_nvtx',
            dirname = args.dir + subfolder,
            )

    for s in suffixes:

        for r in config['Regions']:
            region = config['Regions'][r]
            eta_range = "eta{}to{}".format(region[0], region[1]).replace(".","p")
            eta_label = '{{{} #leq | #eta^{{e}}(reco)| < {}}}'.format(region[0], region[1])

            #print(r)
            #print(region)
            #print(eta_range)
            #print(eta_label)

            if config['Efficiency']:

                # Efficiency vs Run Number
                drawplots.makeeff(
                    inputFiles_list = [input_file],
                    saveplot = True,
                    dirname = args.dir + subfolder,
                    nvtx_suffix = s,
                    den = ['h_PlateauEffVsRunNb_Denominator_EGNonIso_plots_{}'.format(eta_range)],
                    num = ['h_PlateauEffVsRunNb_Numerator_{}_plots_{}'.format(iso, eta_range) for iso in config['Isos']],
                    xtitle = 'run number',
                    ytitle = 'L1EG30 Efficiency',
                    axisranges = [0, 1, 0.8, 1.05],
                    legendlabels = [label(iso) for iso in config['Isos']],
                    extralabel = "#splitline{"+eventselection+", p_{{T}}^{{e}}(reco) #geq 35 GeV}}{}".format(eta_label),
                    top_label = toplabel,
                    plotname = "L1EG_EffVsRunNb_{}".format(r),
                    )

            for iso in config['Isos']:
                if config['TurnOns']:
                    
                    # Efficiency vs pT
                    # all eta ranges and all qualities
                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(iso, eta_range)],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for thr in  config['Thresholds']],
                        xtitle = 'p_{T}^{e}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = ['p_{{T}}^{{L1 e}} #geq {} GeV'.format(thr) for thr in config['Thresholds']],
                        #axisranges = [0, 500],
                        extralabel = "#splitline{"+eventselection+", {}}}{}".format(label(iso), eta_label),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname + '_L1EG_TurnOn{}_{}'.format(iso, r) ,
                        )

                    # same thing, zoom on the 0 - 50 GeV region in pT
                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(iso, eta_range)],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for thr in  config['Thresholds']],
                        xtitle = 'p_{T}^{e}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = ['p_{{T}}^{{L1 e}} #geq {} GeV'.format(thr) for thr in config['Thresholds']],
                        axisranges = [5, 50],
                        extralabel = "#splitline{"+eventselection+", {}}}{}".format(label(iso), eta_label),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname + '_L1EG_TurnOn{}_{}_Zoom'.format(iso, r) ,
                        )

                    # Comparisons between bins of PU:
                    if config['PU_plots']['make_histos'] and s == '':
                        bins = config['PU_plots']['nvtx_bins']
                        for thr in config['PU_plots']['draw_thresholds']:
                            drawplots.makeeff(
                                inputFiles_list = [input_file],
                                saveplot = True,
                                dirname = args.dir + subfolder,
                                den = ['h_{}_plots_{}{}'.format(iso, eta_range, suf) for suf in suffixes[1:]],
                                num = ['h_{}_plots_{}_l1thrgeq{}{}'.format(iso, eta_range, thr, suf) for suf in suffixes[1:]],
                                xtitle = 'p_{T}^{e}(reco) (GeV)',
                                ytitle = 'Efficiency',
                                legendlabels = ['{} #leq nvtx < {}'.format(bins[i], bins[i+1]) for i in range(len(bins)-1)],
                                #axisranges = [3, 300],
                                extralabel = "#splitline{"+eventselection+", {}}}{}".format(label(iso), eta_label),
                                setlogx = True,
                                top_label = toplabel,
                                plotname = channelname + '_L1EG{}_TurnOn{}_{}_vsPU'.format(thr, iso, r) ,
                                )

            if config['TurnOns']:

                # Efficiency vs pT
                # Comparison between isos
                for thr in [15, 30]:
                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(iso, eta_range) for iso in config['Isos']],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for iso in config['Isos']],
                        xtitle = 'p_{T}^{e}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = [iso for iso in config['Isos']],
                        #axisranges = [3, 1000],
                        extralabel = "#splitline{"+eventselection+", All qual.}}{{p_{{T}}^{{L1 EG}} #geq {} GeV, {}}}".format(thr, eta_label[1:-1]),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname + '_L1EG{}_TurnOn_{}_IsoComparison'.format(thr, r) ,
                        )

                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(iso, eta_range) for iso in config['Isos']],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for iso in config['Isos']],
                        xtitle = 'p_{T}^{e}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = [iso for iso in config['Isos']],
                        axisranges = [5, 50],
                        extralabel = "#splitline{"+eventselection+", All qual.}}{{p_{{T}}^{{L1 EG}} #geq {} GeV, {}}}".format(thr, eta_label[1:-1]),
                        #setlogx = True,
                        top_label = toplabel,
                        plotname = channelname + '_L1EG{}_TurnOn_{}_IsoComparison_Zoom'.format(thr, r) ,
                        )

        if config['Efficiency']:
            # Efficiency vs Eta Phi
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['h_EG25_EtaPhi_NumeratorEGNonIso'],
                den = ['h_EG25_EtaPhi_DenominatorEGNonIso'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG25 efficiency (p_{T}^{e}(reco) > 30 GeV)',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+'}{L1 EG NonIso}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_EffVsEtaPhi',
                axisranges = [-2.5, 2.5, -3.1416, 3.1416, 0, 1.1],
                )

        if config['Prefiring']:
            # Postfiring vs Eta 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_eta'],
                den = ['L1EG20_AllEvents_Denominator_eta'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (All events) 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_eta'],
                den = ['L1EG20_AllEvents_Denominator_eta'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_eta'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_eta'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_eta'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_eta'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )










            # Postfiring vs Runnb 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_runnb'],
                den = ['L1EG20_AllEvents_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsRunnb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Runnb (All events) 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_runnb'],
                den = ['L1EG20_AllEvents_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsRunnb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Runnb (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_runnb'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsRunnb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Runnb (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_runnb'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsRunnb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )







            # Postfiring vs Eta Phi
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_etaphi'],
                den = ['L1EG20_AllEvents_Denominator_etaphi'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (All events)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_etaphi'],
                den = ['L1EG20_AllEvents_Denominator_etaphi'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_etaphi'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_etaphi'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_etaphi'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_etaphi'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )


            # Postfiring vs Eta Pt
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_etapt'],
                den = ['L1EG20_AllEvents_Denominator_etapt'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsEtaPt',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
            )

            # Prefiring vs Eta Pt (All events)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_etapt'],
                den = ['L1EG20_AllEvents_Denominator_etapt'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsEtaPt',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
                )

            # Prefiring vs Eta Pt (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_etapt'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_etapt'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsEtaPt',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
                )

            # Prefiring vs Eta Pt (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_etapt'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_etapt'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsEtaPt',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
                )


            # Prefiring vs M(ll)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['mll_unpref_trigrules_L1FinalORBXmin1_barrelbarrel', 'mll_unpref_1stbx_L1FinalORBXmin1_barrelbarrel'],
                den = ['mll_unpref_trigrules_barrelbarrel', 'mll_unpref_1stbx_barrelbarrel'],
                xtitle = 'M(e_{1}e_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-1',
                legendlabels = ['Unpref events (trig. rules)', 'Unpref events (1st bx)'],
                extralabel = '#splitline{'+eventselection+', |#eta(e_{1}, e_{2})|<1.479}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_mll_unpref_L1FinalORBXmin1_barrelbarrel',
                axisranges = [50, 3000, 0, 0.1],
                )

            # Prefiring vs M(ll)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['mll_unpref_trigrules_L1FinalORBXmin2_barrelbarrel'],
                den = ['mll_unpref_trigrules_barrelbarrel'],
                xtitle = 'M(e_{1}e_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-2',
                legendlabels = ['Unpref events (trig. rules)'],
                extralabel = '#splitline{'+eventselection+', |#eta(e_{1}, e_{2})|<1.479}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_mll_unpref_L1FinalORBXmin2_barrelbarrel',
                axisranges = [50, 3000, 0, 0.1],
                )

            # Prefiring vs M(ll)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['mll_unpref_trigrules_L1FinalORBXmin1_endcapendcap', 'mll_unpref_1stbx_L1FinalORBXmin1_endcapendcap'],
                den = ['mll_unpref_trigrules_endcapendcap', 'mll_unpref_1stbx_endcapendcap'],
                xtitle = 'M(e_{1}e_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-1',
                legendlabels = ['Unpref events (trig. rules)', 'Unpref events (1st bx)'],
                extralabel = '#splitline{'+eventselection+', |#eta(e_{1}, e_{2})|>1.479}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_mll_unpref_L1FinalORBXmin1_endcapendcap',
                axisranges = [50, 3000, 0, 0.1],
                )

            # Prefiring vs M(ll)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['mll_unpref_trigrules_L1FinalORBXmin2_endcapendcap'],
                den = ['mll_unpref_trigrules_endcapendcap'],
                xtitle = 'M(e_{1}e_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-2',
                legendlabels = ['Unpref events (trig. rules)'],
                extralabel = '#splitline{'+eventselection+', |#eta(e_{1}, e_{2})|>1.479}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_mll_unpref_L1FinalORBXmin2_endcapendcap',
                axisranges = [50, 3000, 0, 0.1],
                )


            # Postfiring vs Eta 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_eta_fwd'],
                den = ['L1EG20_AllEvents_Denominator_eta_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsEta_Fwd',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (All events) 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_eta_fwd'],
                den = ['L1EG20_AllEvents_Denominator_eta_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsEta_Fwd',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_eta_fwd'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_eta_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsEta_Fwd',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_eta_fwd'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_eta_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsEta_Fwd',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )


            # Postfiring vs Eta Phi
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_etaphi_fwd'],
                den = ['L1EG20_AllEvents_Denominator_etaphi_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsEtaPhi_Fwd',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (All events)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_etaphi_fwd'],
                den = ['L1EG20_AllEvents_Denominator_etaphi_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsEtaPhi_Fwd',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_etaphi_fwd'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_etaphi_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsEtaPhi_Fwd',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_etaphi_fwd'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_etaphi_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = '#phi^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsEtaPhi_Fwd',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )


            # Postfiring vs Eta Pt
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxplus1_etapt_fwd'],
                den = ['L1EG20_AllEvents_Denominator_etapt_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PostfiringVsEtaPt_Fwd',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
            )

            # Prefiring vs Eta Pt (All events)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_AllEvents_bxmin1_etapt_fwd'],
                den = ['L1EG20_AllEvents_Denominator_etapt_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_AllEvents_PrefiringVsEtaPt_Fwd',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
                )

            # Prefiring vs Eta Pt (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_etapt_fwd'],
                den = ['L1EG20_L1_UnprefireableEvent_FirstBxInTrain_Denominator_etapt_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_FirstBxInTrain_PrefiringVsEtaPt_Fwd',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
                )

            # Prefiring vs Eta Pt (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1EG20_L1_UnprefireableEvent_TriggerRules_bxmin1_etapt_fwd'],
                den = ['L1EG20_L1_UnprefireableEvent_TriggerRules_Denominator_etapt_fwd'],
                xtitle = '#eta^{e}(reco)',
                ytitle = 'p_{T}^{e}(reco)',
                ztitle = 'L1EG20 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}(e)>25 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname + '_L1EG_UnprefireableEvent_TriggerRules_PrefiringVsEtaPt_Fwd',
                axisranges = [-5, 5, 50, 4000, 0, 0.1],
                addnumtoden = False,
                setlogy = True,
                )


            
        if config['Response'] and 'EGNonIso' in config['Isos']:

            regions = config['Regions'].values()
            eta_ranges = ["eta{}to{}".format(region[0], region[1]).replace(".","p") for region in regions]
            eta_labels = ['{} #leq | #eta| < {}'.format(region[0], region[1]) for region in regions]

            # Resolution Vs Pt
            drawplots.makeresol(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                h2d = ['h_ResponseVsPt_EGNonIso_plots_{}'.format(eta_range) for eta_range in eta_ranges],
                xtitle = 'p_{T}^{reco e} (GeV)',
                ytitle = '(p_{T}^{L1EG}/p_{T}^{reco e})',
                extralabel = '#splitline{'+eventselection+'}{Non Iso.}',
                legendlabels = eta_labels,
                top_label = toplabel,
                plotname = channelname + '_L1EG_ResponseVsPt',
                axisranges = [0, 100, 0.8, 1.2], 
                )

            # Resolution Vs RunNb
            drawplots.makeresol(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                h2d = ['h_ResponseVsRunNb_EGNonIso_plots_{}'.format(eta_range) for eta_range in eta_ranges],
                xtitle = 'run number',
                ytitle = '(p_{T}^{L1EG}/p_{T}^{reco e})',
                extralabel = '#splitline{'+eventselection+'}{Non Iso.}',
                legendlabels = eta_labels,
                top_label = toplabel,
                plotname = channelname + '_L1EG_ResponseVsRunNb',
                axisranges = [355374, 362760, 0.8, 1.2],
                )


def label(iso):
    labels = {
            'EGNonIso': 'Non iso',
            'EGLooseIso': 'Loose iso',
            'EGTightIso': 'Tight iso',
            }

    if iso in labels:
        return(labels[iso])
    else:
        return('')

if __name__ == '__main__':
    main()
