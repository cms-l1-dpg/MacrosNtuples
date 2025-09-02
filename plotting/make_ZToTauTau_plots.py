eventselection='#mu+#tau_{h}'
subfolder='/plots_ztotautau'
channelname='ZToTauTau'

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
    parser.add_argument("-c", "--config", dest="config", help="The YAML config to read from", type=str, default='../config_cards/full_ZToTauTau.yaml')
    parser.add_argument("-l", "--lumi", dest="lumi", help="The integrated luminosity to display in the top right corner of the plot", type=str, default='')
    
    args = parser.parse_args()
    config = yaml.safe_load(open(args.config, 'r'))
    
    input_file = args.dir + "/all_ZToTauTau.root"
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
        saveroot = False,
        h1d = ['h_nvtx'],
        xtitle = 'N_{vtx}',
        ytitle = 'Events',
        top_label = toplabel,
        plotname = channelname+'_L1Tau_nvtx',
        dirname = args.dir + subfolder,
    )
    
    
    for s in suffixes:
        
        for r in config['Regions']:
            region = config['Regions'][r]
            eta_range = "eta{}to{}".format(region[0], region[1]).replace(".","p")
            eta_label = '{'+'{}'.format(region[0])+ '#leq | #eta^{#tau_{h}}(reco)| < '+'{}'.format(region[1])+'}'

            if config['Efficiency']:
                
                # Efficiency vs Run Number
                drawplots.makeeff(
                    inputFiles_list = [input_file],
                    saveplot = True,
                    dirname = args.dir + subfolder,
                    nvtx_suffix = s,
                    den = ['h_PlateauEffVsRunNb_Denominator_TauNonIso_plots_{}'.format(eta_range)],
                    num = ['h_PlateauEffVsRunNb_Numerator_{}_plots_{}'.format(iso, eta_range) for iso in config['Isos']],
                    xtitle = 'run number',
                    ytitle = 'L1Tau30 Efficiency',
                    axisranges = [0, 1, 0.5, 1.05],
                    legendlabels = [label(iso) for iso in config['Isos']],
                    extralabel = "#splitline{"+eventselection+", p_{T}^{#tau_{h}}(reco) #geq 40 GeV}"+"{}".format(eta_label),
                    top_label = toplabel,
                    plotname = "L1Tau_EffVsRunNb_{}".format(r),
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
                        xtitle = 'p_{T}^{#tau_{h}}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = ['p_{T}^{L1 Tau} '+'#geq {} GeV'.format(thr) for thr in config['Thresholds']],
                        axisranges = [20, 500],
                        extralabel = "#splitline{"+eventselection+", {}".format(label(iso))+"}"+"{}".format(eta_label),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname+'_L1Tau_TurnOn{}_{}'.format(iso, r) ,
                    )
                    #Zoom
                    drawplots.makeeff(
                        inputFiles_list = [input_file],
                        saveplot = True,
                        dirname = args.dir + subfolder,
                        nvtx_suffix = s,
                        den = ['h_{}_plots_{}'.format(iso, eta_range)],
                        num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for thr in  config['Thresholds']],
                        xtitle = 'p_{T}^{#tau_{h}}(reco) (GeV)',
                        ytitle = 'Efficiency',
                        legendlabels = ['p_{T}^{L1 Tau} '+'#geq {} GeV'.format(thr) for thr in config['Thresholds']],
                        axisranges = [20, 50],
                        extralabel = "#splitline{"+eventselection+", {}".format(label(iso))+"}"+"{}".format(eta_label),
                        setlogx = True,
                        top_label = toplabel,
                        plotname = channelname+'_L1Tau_TurnOn{}_{}_Zoom'.format(iso, r) ,
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
                                xtitle = 'p_{T}^{#tau_{h}}(reco) (GeV)',
                                ytitle = 'Efficiency',
                                legendlabels = ['{} #leq nvtx < {}'.format(bins[i], bins[i+1]) for i in range(len(bins)-1)],
                                axisranges = [20, 500],
                                extralabel = "#splitline{"+eventselection+", {}".format(label(iso))+"}"+"{}".format(eta_label),
                                setlogx = True,
                                top_label = toplabel,
                                plotname = channelname+'_L1Tau{}_TurnOn{}_{}_vsPU'.format(thr, iso, r) ,
                            )
                            
                if config['TurnOns']:
                    # Efficiency vs pT 
                    # Comparison between isos
                    for thr in [26, 34]:
                        drawplots.makeeff(
                            inputFiles_list = [input_file],
                            saveplot = True,
                            dirname = args.dir + subfolder,
                            nvtx_suffix = s,
                            den = ['h_{}_plots_{}'.format(iso, eta_range) for iso in config['Isos']],
                            num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for iso in config['Isos']],
                            xtitle = 'p_{T}^{#tau_{h}}(reco) (GeV)',
                            ytitle = 'Efficiency',
                            legendlabels = [iso for iso in config['Isos']],
                            axisranges = [20, 500],
                            extralabel = "#splitline{"+eventselection+"}"+"{p_{T}^{L1 Tau} #geq "+"{}".format(thr)+" GeV, "+"{}".format(eta_label[1:-1])+"}",
                            setlogx = True,
                            top_label = toplabel,
                            plotname = channelname+'_L1Tau{}_TurnOn_{}_IsoComparison'.format(thr, r) ,
                        )
                        
                        drawplots.makeeff(
                            inputFiles_list = [input_file],
                            saveplot = True,
                            dirname = args.dir + subfolder,
                            nvtx_suffix = s,
                            den = ['h_{}_plots_{}'.format(iso, eta_range) for iso in config['Isos']],
                            num = ['h_{}_plots_{}_l1thrgeq{}'.format(iso, eta_range, thr) for iso in config['Isos']],
                            xtitle = 'p_{T}^{#tau_{h}}(reco) (GeV)',
                            ytitle = 'Efficiency',
                            legendlabels = [iso for iso in config['Isos']],
                            axisranges = [20, 50],
                            extralabel = "#splitline{"+eventselection+"}"+"{p_{T}^{L1 Tau} #geq "+"{}".format(thr)+" GeV, "+"{}".format(eta_label[1:-1])+"}",
                            top_label = toplabel,
                            plotname = channelname+'_L1Tau{}_TurnOn_{}_IsoComparison_Zoom'.format(thr, r) ,
                        )
                    
        if config['Efficiency']:
            # Efficiency vs Eta Phi 
            drawplots.makeeff(
                inputFiles_list = [input_file],
                saveplot = True,
                dirname = args.dir + subfolder,
                nvtx_suffix = s,
                num = ['h_Tau30_EtaPhi_NumeratorTauNonIso'],
                den = ['h_Tau30_EtaPhi_DenominatorTauNonIso'],
                xtitle = '#eta^{#tau_{h}}(reco)',
                ytitle = '#phi^{#tau_{h}}(reco)',
                ztitle = 'L1Tau30 efficiency (p_{T}^{#tau_{h}}(reco) > 40 GeV)',
                legendlabels = [''],
                extralabel = '#splitline{'+eventselection+'}{L1 Tau NonIso}',
                top_label = toplabel,
                plotname = channelname+'_L1Tau_EffVsEtaPhi',
                axisranges = [-2.5, 2.5, -3.1416, 3.1416, 0, 1.1],
            )
            
            
            
        if config['Response'] and 'TauNonIso' in config['Isos']:
           regions = config['Regions'].values()
           eta_ranges = ["eta{}to{}".format(region[0], region[1]).replace(".","p") for region in regions]
           eta_labels = ['{} #leq | #eta| < {}'.format(region[0], region[1]) for region in regions]
           
           # Resolution Vs Pt 
           drawplots.makeresol(
               inputFiles_list = [input_file],
               saveplot = True,
               dirname = args.dir + subfolder,
               nvtx_suffix = s,
               h2d = ['h_ResponseVsPt_TauNonIso_plots_{}'.format(eta_range) for eta_range in eta_ranges],
               xtitle = 'p_{T}^{#tau_{h}}(reco) (GeV)',
               ytitle = '(p_{T}^{L1Tau}/p_{T}^{#tau_{h}}(reco))',
               extralabel = '#splitline{'+eventselection+'}{Non Iso.}',
               legendlabels = eta_labels,
               top_label = toplabel,
               plotname = channelname+'_L1Tau_ResponseVsPt',
               axisranges = [20, 70, 0.8, 1.2],
           )

           # Resolution Vs RunNb 
           drawplots.makeresol(
               inputFiles_list = [input_file],
               saveplot = True,
               dirname = args.dir + subfolder,
               nvtx_suffix = s,
               h2d = ['h_ResponseVsRunNb_TauNonIso_plots_{}'.format(eta_range) for eta_range in eta_ranges],
               xtitle = 'run number',
               ytitle = '(p_{T}^{L1Tau}/p_{T}^{#tau_{h}}(reco))',
               extralabel = '#splitline{'+eventselection+'}{Non Iso.}',
               legendlabels = eta_labels,
               top_label = toplabel,
               plotname = channelname+'_L1Tau_ResponseVsRunNb',
               axisranges = [355374, 362760, 0.8, 1.2],
           )
           








            
def label(iso):
    labels = {
            'TauNonIso': 'Non Iso',
            'TauIso': 'Iso',
            }

    if iso in labels:
        return(labels[iso])
    else:
        return('')

            

if __name__ == '__main__':
    main()
