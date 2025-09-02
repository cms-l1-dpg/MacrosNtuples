# make_mu_plots.py, a program to draw the L1Studies plots obtained from the histograms extracted from NanoAOD
eventselection='Z#rightarrow #mu#mu'
subfolder='/plots_ztomumu'
channelname='ZToMuMu'

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
    parser.add_argument("-c", "--config", dest="config", help="The YAML config to read from", type=str, default='../config_cards/full_ZToMuMu.yaml')
    parser.add_argument("-l", "--lumi", dest="lumi", help="The integrated luminosity to display in the top right corner of the plot", type=str, default='')

    args = parser.parse_args()
    config = yaml.safe_load(open(args.config, 'r'))

    input_file = args.dir + "/all_ZToMuMu.root"
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
            plotname = channelname+'_L1Mu_nvtx',
            dirname = args.dir + subfolder,
            )

    for s in suffixes:

        for r in config['Regions']:
            region = config['Regions'][r]
            eta_range = "eta{}to{}".format(region[0], region[1]).replace(".","p")
            eta_label = '{{{} #leq | #eta^{{#mu}}(reco)| < {}}}'.format(region[0], region[1])

            if config['Efficiency']:

                # Efficiency vs Run Number
                drawplots.makeeff(
                    inputFiles_list = [input_file],
                    saveplot = True,
                    dirname = args.dir + subfolder,
                    nvtx_suffix = s,
                    den = ['h_PlateauEffVsRunNb_Denominator_AllQual_plots_{}'.format(eta_range)],
                    num = ['h_PlateauEffVsRunNb_Numerator_{}_plots_{}'.format(qual, eta_range) for qual in config['Qualities']],
                    xtitle = 'run number',
                    ytitle = 'L1Mu22 Efficiency',
                    axisranges = [0, 1, 0.8, 1.05],
                    legendlabels = [label(qual) for qual in config['Qualities']],
                    extralabel = "#splitline{"+eventselection+", p_{{T}}^{{#mu}}(reco) #geq 27 GeV}}{}".format(eta_label),
                    top_label = toplabel,
                    plotname = "L1Mu_EffVsRunNb_{}".format(r),
                    )

            for qual in config['Qualities']:
                if config['TurnOns']:

                    # Efficiency vs pT
                    # all eta ranges and all qualities
                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(qual, eta_range)],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(qual, eta_range, thr) for thr in  config['Thresholds']],
                        xtitle = 'p_{T}^{#mu}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = ['p_{{T}}^{{L1 #mu}} #geq {} GeV'.format(thr) for thr in config['Thresholds']],
                        axisranges = [3, 1000],
                        extralabel = "#splitline{"+eventselection+", {}}}{}".format(label(qual), eta_label),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname+'_L1Mu_TurnOn{}_{}'.format(qual, r) ,
                        )

                    # same thing, zoom on the 0 - 50 GeV region in pT
                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(qual, eta_range)],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(qual, eta_range, thr) for thr in  config['Thresholds']],
                        xtitle = 'p_{T}^{#mu}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = ['p_{{T}}^{{L1 #mu}} #geq {} GeV'.format(thr) for thr in config['Thresholds']],
                        axisranges = [3, 50],
                        extralabel = "#splitline{"+eventselection+", {}}}{}".format(label(qual), eta_label),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname+'_L1Mu_TurnOn{}_{}_Zoom'.format(qual, r) ,
                        )

                    # Comparisons between bins of PU:
                    if config['PU_plots']['make_histos'] and s == '':
                        bins = config['PU_plots']['nvtx_bins']
                        for thr in config['PU_plots']['draw_thresholds']:
                            drawplots.makeeff(
                                inputFiles_list = [input_file],
                                saveplot = True,
                                dirname = args.dir + subfolder,
                                den = ['h_{}_plots_{}{}'.format(qual, eta_range, suf) for suf in suffixes[1:]],
                                num = ['h_{}_plots_{}_l1thrgeq{}{}'.format(qual, eta_range, thr, suf) for suf in suffixes[1:]],
                                xtitle = 'p_{T}^{#mu}(reco) (GeV)',
                                ytitle = 'Efficiency',
                                legendlabels = ['{} #leq nvtx < {}'.format(bins[i], bins[i+1]) for i in range(len(bins)-1)],
                                axisranges = [3, 1000],
                                extralabel = "#splitline{"+eventselection+", {}}}{}".format(label(qual), eta_label),
                                setlogx = True,
                                top_label = toplabel,
                                plotname = channelname+'_L1Mu{}_TurnOn{}_{}_vsPU'.format(thr, qual, r) ,
                                )

        if config['Efficiency']:
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['h_Mu22_EtaPhi_NumeratorQual12'],
                den = ['h_Mu22_EtaPhi_DenominatorQual12'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = '#phi^{#mu}(reco)',
                ztitle = 'L1Mu22 efficiency (p_{T}^{#mu}(reco) > 27 GeV)',
                legendlabels = [''],
                extralabel = '#splitline{"+eventselection+"}{L1 Qual. #geq 12}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu22_EffVsEtaPhi',
                axisranges = [-2.4, 2.4, -3.1416, 3.1416, 0, 1.1],
                )

        if config['Prefiring']:

            # Postfiring vs Eta 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxplus1_eta'],
                den = ['L1Mu10_AllEvents_Denominator_eta'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'L1Mu10 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PostfiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (All events) 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxmin1_eta'],
                den = ['L1Mu10_AllEvents_Denominator_eta'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PrefiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_eta'],
                den = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_Denominator_eta'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_FirstBxInTrain_PrefiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_bxmin1_eta'],
                den = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_Denominator_eta'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_TriggerRules_PrefiringVsEta',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )



            # Postfiring vs RunNb 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxplus1_runnb'],
                den = ['L1Mu10_AllEvents_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1Mu10 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PostfiringVsRunNb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs RunNb (All events) 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxmin1_runnb'],
                den = ['L1Mu10_AllEvents_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PrefiringVsRunNb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs RunNb (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_runnb'],
                den = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_FirstBxInTrain_PrefiringVsRunNb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs RunNb (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_bxmin1_runnb'],
                den = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_Denominator_runnb'],
                xtitle = 'Run number',
                ytitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_TriggerRules_PrefiringVsRunNb',
                axisranges = [-5, 5, 0, 0.1],
                addnumtoden = False,
                )



            # Postfiring vs Eta Phi
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxplus1_etaphi'],
                den = ['L1Mu10_AllEvents_Denominator_etaphi'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = '#phi^{#mu}(reco)',
                ztitle = 'L1Mu10 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PostfiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (All events)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxmin1_etaphi'],
                den = ['L1Mu10_AllEvents_Denominator_etaphi'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = '#phi^{#mu}(reco)',
                ztitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PrefiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (UnprefireableEvent_FirstBxInTrain)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_etaphi'],
                den = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_Denominator_etaphi'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = '#phi^{#mu}(reco)',
                ztitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_FirstBxInTrain_PrefiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )

            # Prefiring vs Eta Phi (UnprefireableEvent_TriggerRules)
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_bxmin1_etaphi'],
                den = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_Denominator_etaphi'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = '#phi^{#mu}(reco)',
                ztitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_TriggerRules_PrefiringVsEtaPhi',
                axisranges = [-5, 5, -3.1416, 3.1416, 0, 0.1],
                addnumtoden = False,
                )


            # Postfiring vs Eta Pt
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['L1Mu10_AllEvents_bxplus1_etapt'],
                den = ['L1Mu10_AllEvents_Denominator_etapt'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'p_{T}^{jet}(reco)',
                ztitle = 'L1Mu10 (BX+1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PostfiringVsEtaPt',
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
                num = ['L1Mu10_AllEvents_bxmin1_etapt'],
                den = ['L1Mu10_AllEvents_Denominator_etapt'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'p_{T}^{jet}(reco)',
                ztitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{All events}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_AllEvents_PrefiringVsEtaPt',
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
                num = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_bxmin1_etapt'],
                den = ['L1Mu10_L1_UnprefireableEvent_FirstBxInTrain_Denominator_etapt'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'p_{T}^{jet}(reco)',
                ztitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (1st bx in train)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_FirstBxInTrain_PrefiringVsEtaPt',
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
                num = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_bxmin1_etapt'],
                den = ['L1Mu10_L1_UnprefireableEvent_TriggerRules_Denominator_etapt'],
                xtitle = '#eta^{#mu}(reco)',
                ytitle = 'p_{T}^{jet}(reco)',
                ztitle = 'L1Mu10 (BX-1) matching fraction',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+', p_{T}^{#mu}(reco) > 20 GeV}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_L1Mu_UnprefireableEvent_TriggerRules_PrefiringVsEtaPt',
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
                xtitle = 'M(#mu_{1}#mu_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-1',
                legendlabels = ['Unpref events (trig. rules)', 'Unpref events (1st bx)'],
                extralabel = '#splitline{'+eventselection+', |#eta(#mu_{1}, #mu_{2})|<1.24}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_mll_unpref_L1FinalORBXmin1_barrelbarrel',
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
                xtitle = 'M(#mu_{1}#mu_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-2',
                legendlabels = ['Unpref events (trig. rules)'],
                extralabel = '#splitline{'+eventselection+', |#eta(#mu_{1}, #mu_{2})|<1.24}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_mll_unpref_L1FinalORBXmin2_barrelbarrel',
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
                xtitle = 'M(#mu_{1}#mu_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-1',
                legendlabels = ['Unpref events (trig. rules)', 'Unpref events (1st bx)'],
                extralabel = '#splitline{'+eventselection+', |#eta(#mu_{1}, #mu_{2})|>1.24}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_mll_unpref_L1FinalORBXmin1_endcapendcap',
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
                xtitle = 'M(#mu_{1}#mu_{2}) (GeV)',
                ytitle = 'Fraction of events passing L1FinalOR in BX-2',
                legendlabels = ['Unpref events (trig. rules)'],
                extralabel = '#splitline{'+eventselection+', |#eta(#mu_{1}, #mu_{2})|>1.24}{Unpref. events (trig. rules)}',
                top_label = toplabel,
                plotname = channelname+'_mll_unpref_L1FinalORBXmin2_endcapendcap',
                axisranges = [50, 3000, 0, 0.1],
                )



        if config['Response'] and 'AllQual' in config['Qualities']:

            regions = config['Regions'].values()
            eta_ranges = ["eta{}to{}".format(region[0], region[1]).replace(".","p") for region in regions]
            eta_labels = ['{} #leq | #eta| < {}'.format(region[0], region[1]) for region in regions]

            # Resolution Vs Pt
            drawplots.makeresol(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                h2d = ['h_ResponseVsPt_AllQual_plots_{}'.format(eta_range) for eta_range in eta_ranges],
                xtitle = 'p_{T}^{reco muon} (GeV)',
                ytitle = '(p_{T}^{L1Mu}/p_{T}^{reco muon})',
                extralabel = '#splitline{'+eventselection+'}{All qual.}',
                legendlabels = eta_labels,
                top_label = toplabel,
                plotname = channelname+'_L1Mu_ResponseVsPt',
                axisranges = [0, 100, 0.8, 1.6], 
                )

            # Resolution Vs RunNb
            drawplots.makeresol(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                h2d = ['h_ResponseVsRunNb_AllQual_plots_{}'.format(eta_range) for eta_range in eta_ranges],
                xtitle = 'run number',
                ytitle = '(p_{T}^{L1Mu}/p_{T}^{reco muon})',
                extralabel = '#splitline{'+eventselection+'}{All qual.}',
                legendlabels = eta_labels,
                top_label = toplabel,
                plotname = channelname+'_L1Mu_ResponseVsRunNb',
                axisranges = [355374, 362760, 0.9, 1.5],
                )

        if config['TurnOns'] and 'Qual12' in config['Qualities']:

            regions = config['Regions'].values()
            eta_ranges = ["eta{}to{}".format(region[0], region[1]).replace(".","p") for region in regions]
            eta_labels = ['{} #leq | #eta| < {}'.format(region[0], region[1]) for region in regions]

            # Efficiency vs pT
            # Comparison between track finders
            for thr in [5, 22]:
                drawplots.makeeff(
                    inputFiles_list = [input_file],
                    saveplot = True,
                    dirname = args.dir + subfolder,
                    nvtx_suffix = s,
                    den = ['h_Qual12_plots_{}'.format(eta_range) for eta_range in eta_ranges],
                    num = ['h_Qual12_plots_{}_l1thrgeq{}'.format(eta_range, thr) for eta_range in eta_ranges],
                    xtitle = 'p_{T}^{#mu}(reco) (GeV)',
                    ytitle = 'Efficiency',
                    legendlabels = eta_labels,
                    axisranges = [3, 1000],
                    extralabel = "#splitline{"+eventselection+", All qual.}}{{p_{{T}}^{{L1 #mu}} #geq {} GeV}}".format(thr),
                    setlogx = True,
                    top_label = toplabel,
                    plotname = channelname+'_L1Mu{}_TurnOnQual12_EtaComparison'.format(thr) ,
                    )

                drawplots.makeeff(
                    inputFiles_list = [input_file],
                    saveplot = True,
                    dirname = args.dir + subfolder,
                    nvtx_suffix = s,
                    den = ['h_Qual12_plots_{}'.format(eta_range) for eta_range in eta_ranges],
                    num = ['h_Qual12_plots_{}_l1thrgeq{}'.format(eta_range, thr) for eta_range in eta_ranges],
                    xtitle = 'p_{T}^{#mu}(reco) (GeV)',
                    ytitle = 'Efficiency',
                    legendlabels = eta_labels,
                    axisranges = [3, 50],
                    extralabel = "#splitline{"+eventselection+", All qual.}}{{p_{{T}}^{{L1 #mu}} #geq {} GeV}}".format(thr),
                    #setlogx = True,
                    top_label = toplabel,
                    plotname = channelname+'_L1Mu{}_TurnOnQual12_EtaComparison_Zoom'.format(thr) ,
                    )

def label(qual):
    labels = {
            'AllQual': 'All qual.',
            'Qual8': 'Qual. #geq 8',
            'Qual12': 'Qual. #geq 12',
            }

    if qual in labels:
        return(labels[qual])
    else:
        return('')

if __name__ == '__main__':
    main()
