import ROOT
import yaml
import json
from array import array
from math import floor, ceil
import numpy as np
from bins import *

response_bins = array('f',[0.+float(i)/100. for i in range(200)] )

runnb_bins = None

def set_runnb_bins(df):
    global runnb_bins
    if runnb_bins is None:
        # +1: to get [run, run+1] bin, +0.5 and floor to prevent float rounding errors + high bound
        # in range is excluded, so feed run, and run+2 to get [run, run+1]
        runNb_max = ceil(df.Max("run").GetValue() + 1.5)
        runNb_min = floor(df.Min("run").GetValue())
        runnb_bins = array('f', [r for r in range(runNb_min, runNb_max)])
    else:
        print("runnb_bins are already set")

config = None
def set_config(stream):
    global config
    if config is None:
        config = yaml.safe_load(stream)
    else:
        print("config_dict is already set")

def make_filter(golden_json):
    fltr = ''
    if golden_json != '':
        with open(golden_json) as j:
            J = json.load(j)
        for run_nb in J:
            fltr += '(run=={}&&('.format(run_nb)
            for lumis in J[run_nb]:
                fltr += '(luminosityBlock>={}&&luminosityBlock<={})||'.format(lumis[0], lumis[1])
            fltr = fltr[:-2] + '))||'

        fltr = fltr[:-2]
    return(fltr)



#String printing stuff for a few events
stringToPrint = '''
if(EventsToPrint <100) {

cout << "*********New Event********"<<endl;
cout << "run " << run<<endl;

for(unsigned int i = 0;i< (_lPt).size();i++ ){
cout << "Lepton Pt, Eta, Phi: " << (_lPt)[i]<<", "<<(_lEta)[i]<<", "<<(_lPhi)[i]<<endl;
cout << "Lepton pdgId: " << (_lpdgId)[i]<<endl;
}
for(unsigned int i = 0;i< (Photon_pt).size();i++ ){
cout << "Photon Pt, Eta, Phi: " << (Photon_pt)[i]<<", "<<(Photon_eta)[i]<<", "<<(Photon_phi)[i]<<endl;
}
for(unsigned int i = 0;i< (Jet_pt).size();i++ ){
cout << "jet Pt, Eta, Phi: " << (Jet_pt)[i]<<", "<<(Jet_eta)[i]<<", "<<(Jet_phi)[i]<<endl;
cout << "MUEF, CEEF, CHEF: " << (Jet_muEF)[i]<<", "<<(Jet_chEmEF)[i]<<", "<<  (Jet_chHEF)[i]<<endl;
}

for(unsigned int i = 0;i< (L1EG_pt).size();i++ ){
cout << "L1 EG Pt, Eta, Phi: " << (L1EG_pt)[i]<<", "<<(L1EG_eta)[i]<<", "<<(L1EG_phi)[i]<<endl;
}

cout << "probe_L1PtoverRecoPt probe_Pt sizes: "<<probe_L1PtoverRecoPt.size()<<", " <<probe_Pt.size()<<endl;
for(unsigned int i = 0;i< probe_Pt.size();i++ ){
cout << "probe_Pt, probe_L1PtoverRecoPt: "<<probe_L1PtoverRecoPt[i]<<", "<<probe_Pt[i]<<endl;
}

cout << "response, denominator_pt sizes: " << response.size()<<", " <<denominator_pt.size()<<endl;
for(unsigned int i = 0;i<response.size() ;i++ ){
cout <<"response, denominator_pt "<<response[i]<<", "<<denominator_pt[i]<<endl; 
} 
cout <<endl;

EventsToPrint++;
} 
return true;
'''


stringToPrintJets = '''
for(unsigned int i = 0;i< (cleanJet_MUEF).size();i++ ){ 
if((cleanJet_MUEF)[i]>0.5){
cout << "jet Pt, Eta, Phi: " << (cleanJet_Pt)[i]<<", "<<(cleanJet_Eta)[i]<<", "<<(cleanJet_Phi)[i]<<", " << (cleanJet_MUEF)[i]<<endl;

}
}
return true;
'''

stringFailingJets = '''

bool findbadjet = false;
for(unsigned int i = 0;i< (cleanJet_MUEF).size();i++ ){
if((cleanJet_Pt)[i]>300&&abs((cleanJet_Eta)[i])<2.5&&cleanJet_L1Pt[i]<50){
cout << "runNb: "<< run<<endl;
cout << "jet Pt, Eta, Phi: " << (cleanJet_Pt)[i]<<", "<<(cleanJet_Eta)[i]<<", "<<(cleanJet_Phi)[i]<< endl; 
cout << "jet NHEF, CHEF, NEEF, CEEF, MUEF: "<<(cleanJet_NHEF)[i]<< ", " << (cleanJet_CHEF)[i]<< ", " << (cleanJet_NEEF)[i]<< ", "<< (cleanJet_CEEF)[i]<< ", " << (cleanJet_MUEF)[i]<<endl;

findbadjet = true;
}
}
if(findbadjet){
for(unsigned int i = 0;i< (L1Jet_pt).size();i++ ){
cout << "L1 JET Pt, Eta, Phi, Bx: " << (L1Jet_pt)[i]<<", "<<(L1Jet_eta)[i]<<", "<<(L1Jet_phi)[i]<< ", "<<(L1Jet_bx)[i]<<endl;
}
}

return true;
'''

stringToPrintHF = '''
if(EventsToPrint <100) {

cout << "*********New Event********"<<endl;
cout << "run " << run<<endl;
cout << "met, met_phi " << PuppiMET_pt <<", "<<PuppiMET_phi<<endl;
for(unsigned int i = 0;i< (_lPt).size();i++ ){
cout << "Lepton Pt, Eta, Phi: " << (_lPt)[i]<<", "<<(_lEta)[i]<<", "<<(_lPhi)[i]<<endl;
cout << "Lepton pdgId: " << (_lpdgId)[i]<<endl;
}
for(unsigned int i = 0;i< (Photon_pt).size();i++ ){
cout << "Photon Pt, Eta, Phi: " << (Photon_pt)[i]<<", "<<(Photon_eta)[i]<<", "<<(Photon_phi)[i]<<endl;
}
for(unsigned int i = 0;i< (Jet_pt).size();i++ ){
cout << "jet Pt, Eta, Phi: " << (Jet_pt)[i]<<", "<<(Jet_eta)[i]<<", "<<(Jet_phi)[i]<<endl;
cout << "MUEF, CEEF, CHEF, NHEF: " <<(Jet_muEF)[i]<<", "<<(Jet_chEmEF)[i]<<", "<<  (Jet_chHEF)[i]<<", "<<  (Jet_neHEF)[i]<<endl;
cout << "jethfsigmaEtaEta jethfsigmaPhiPhi jethfcentralEtaStripSize "<< (Jet_hfsigmaEtaEta)[i]<<", "<<  (Jet_hfsigmaPhiPhi)[i]<<", "<<(Jet_hfcentralEtaStripSize)[i]<<endl;
}


for(unsigned int i = 0;i< (L1Jet_pt).size();i++ ){
cout << "L1 JET Pt, Eta, Phi, Bx: " << (L1Jet_pt)[i]<<", "<<(L1Jet_eta)[i]<<", "<<(L1Jet_phi)[i]<<", " << (L1Jet_bx)[i]<<endl;
}



cout <<endl;

EventsToPrint++;
} 
return true;
'''

highEnergyJet = '''
for( unsigned int i = 0; i < (Jet_pt).size(); i++){
    if(Jet_pt[i] * cosh(Jet_eta[i]) > 6000){
        return false;
    }
}
return true;
'''

def SinglePhotonSelection(df):
    '''
    Select events with exactly one photon with pT>20 GeV.
    The event must pass a photon trigger. 
    '''
#    df = df.Filter('PuppiMET_pt<50')
    df = df.Filter('HLT_Photon110EB_TightID_TightIso')

    df = df.Define('photonsptgt20','Photon_pt>20')
    df = df.Filter('Sum(photonsptgt20)==1','=1 photon with p_{T}>20 GeV')

    df = df.Define('isRefPhoton','Photon_mvaID_WP80&&Photon_electronVeto&&Photon_pt>115&&abs(Photon_eta)<1.479')
    df = df.Filter('Sum(isRefPhoton)==1','Photon has p_{T}>115 GeV, passes tight ID and is in EB')
    
    df = df.Define('cleanPh_Pt','Photon_pt[isRefPhoton]')
    df = df.Define('cleanPh_Eta','Photon_eta[isRefPhoton]')
    df = df.Define('cleanPh_Phi','Photon_phi[isRefPhoton]')
    
    df = df.Define('ref_Pt','cleanPh_Pt[0]')
    df = df.Define('ref_Phi','cleanPh_Phi[0]')
    
    return df
    
def MuonJet_MuonSelection(df):
    '''
    Select events with >= 1 muon with pT>25 GeV.
    The event must pass a single muon trigger. 
    '''
    df = df.Filter('HLT_IsoMu24')

    df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId') 
    df = df.Define('goodmuonPt25','Muon_pt>25&&abs(Muon_pdgId)==13&&Muon_PassTightId')
    df = df.Filter('Sum(goodmuonPt25)>=1','>=1 muon with p_{T}>25 GeV')
    df = df.Define('badmuonPt10','Muon_pt>10&&abs(Muon_pdgId)==13&&Muon_PassTightId==0')
    df = df.Filter('Sum(badmuonPt10)==0','No bad quality muon')

    # reject events containing a jet with energy > 6000 GeV
#    df = df.Filter(highEnergyJet, 'No high energy jet')
    return df
    
def ZEE_EleSelection(df, massmin, massmax):
    '''
    Select Z->ee events passing a single electron trigger. Defines probe pt/eta/phi
    '''
    df = df.Filter('HLT_Ele32_WPTight_Gsf')

    # Trigged on a Electron (probably redondant)
    df = df.Filter('''
    bool trigged_on_e = false;
    for (unsigned int i = 0; i < TrigObj_id.size(); i++){
        if(TrigObj_id[i] == 11) trigged_on_e = true;
    }
    return trigged_on_e;
    ''')

    # TrigObj matching
    df = df.Define('Electron_trig_idx', 'MatchObjToTrig(Electron_eta, Electron_phi, TrigObj_pt, TrigObj_eta, TrigObj_phi, TrigObj_id, 11, TrigObj_filterBits)')
    df = df.Define('Electron_passHLT_Ele32_WPTight_Gsf', 'trig_is_filterbit1_set(Electron_trig_idx, TrigObj_filterBits)')

    df = df.Define('isTag','_lPt>35&&abs(_lpdgId)==11&&Electron_mvaIso_WP90&&Electron_passHLT_Ele32_WPTight_Gsf==true')
    df = df.Filter('Sum(isTag)>0')

    df = df.Define('isProbe','_lPt>5&&abs(_lpdgId)==11&&Electron_mvaIso_WP90&&(Sum(isTag)>=2|| isTag==0)')

    df = df.Define('_mll', 'mll(Electron_pt, Electron_eta, Electron_phi, isTag, isProbe)')
    df = df.Filter('_mll>{}&&_mll<{}'.format(massmin, massmax))

    df = df.Define('probe_Pt','_lPt[isProbe]')
    df = df.Define('probe_Eta','_lEta[isProbe]')
    df = df.Define('probe_Phi','_lPhi[isProbe]')

    df = df.Define('tag_Eta','_lEta[isTag]')

    df = df.Define('barrelbarrel','abs(_lEta[0])<1.479&&abs(_lEta[1])<1.479')
    df = df.Define('endcapendcap','abs(_lEta[0])>1.479&&abs(_lEta[1])>1.479')
    return df


def ZEE_Forward_EleSelection(df, massmin, massmax):

    df = df.Filter('HLT_Ele32_WPTight_Gsf')
    # Trigged on a Electron (probably redondant)
    df = df.Filter('''
    bool trigged_on_e = false;
    for (unsigned int i = 0; i < TrigObj_id.size(); i++){
        if(TrigObj_id[i] == 11) trigged_on_e = true; 
    }
    return trigged_on_e; 
    ''')
    
    # TrigObj matching 
    df = df.Define('Electron_trig_idx', 'MatchObjToTrig(Electron_eta, Electron_phi, TrigObj_pt, TrigObj_eta, TrigObj_phi, TrigObj_id, 11, TrigObj_filterBits)')
    df = df.Define('Electron_passHLT_Ele32_WPTight_Gsf', 'trig_is_filterbit1_set(Electron_trig_idx, TrigObj_filterBits)')

    df = df.Define('isTag','_lPt>35&&abs(_lpdgId)==11&&Electron_mvaIso_WP90&&Electron_passHLT_Ele32_WPTight_Gsf==true')
    df = df.Filter('Sum(isTag)>0')

    df = df.Define('photonsptgt20','Photon_pt>20')
    df = df.Filter('Sum(photonsptgt20)==2','=2 photon with p_{T}>20 GeV')
    df = df.Define('isgoodphoton','Photon_mvaID_WP90&&Photon_pt>25')
    df = df.Define('isforwardphoton','Photon_mvaID_WP90&&Photon_pt>25&&abs(Photon_eta)>2.5')

    df = df.Define('_mll', 'mll(Photon_pt, Photon_eta, Photon_phi, isgoodphoton, isforwardphoton)')
    df = df.Filter('_mll>{}&&_mll<{}'.format(massmin,massmax))

    df = df.Define('probe_Pt','Photon_pt[isforwardphoton]')
    df = df.Define('probe_Eta','Photon_eta[isforwardphoton]')
    df = df.Define('probe_Phi','Photon_phi[isforwardphoton]')

    return df




def ZMuMu_MuSelection(df, massmin, massmax):
    '''
    Selects Z->mumu events passing a single muon trigger. Defines probe pt/eta/phi
    '''
    df = df.Filter('HLT_IsoMu24')

    # Trigged on a Muon (probably redondant)
    df = df.Filter('''
    bool trigged_on_mu = false;
    for (unsigned int i = 0; i < TrigObj_id.size(); i++){
        if(TrigObj_id[i] == 13) trigged_on_mu = true;
    }
    return trigged_on_mu;
    ''')

    # TrigObj matching
    df = df.Define('Muon_trig_idx', 'MatchObjToTrig(Muon_eta, Muon_phi, TrigObj_pt, TrigObj_eta, TrigObj_phi, TrigObj_id, 13, TrigObj_filterBits)')

    df = df.Define('Muon_passHLT_IsoMu24', 'trig_is_filterbit1_set(Muon_trig_idx, TrigObj_filterBits)')
    df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId') 

    df = df.Define('isTag','Muon_pt>25&&abs(Muon_pdgId)==13&&Muon_PassTightId&&Muon_passHLT_IsoMu24')

    df = df.Filter('Sum(isTag)>0')

    df = df.Define('isProbe','Muon_pt>3&&abs(Muon_pdgId)==13&&Muon_PassTightId&& (Sum(isTag)>=2|| isTag==0)')
    df = df.Define('_mll', 'mll(Muon_pt, Muon_eta, Muon_phi, isTag, isProbe)')
    df = df.Define('dr_mll', 'dR_mll(Muon_pt, Muon_eta, Muon_phi, isTag, isProbe)')
    

    df = df.Define('probe_Pt','Muon_pt[isProbe]')
    df = df.Define('probe_Eta','Muon_eta[isProbe]')
    df = df.Define('probe_Phi','Muon_phi[isProbe]')
    df = df.Define('probe_Charge', 'Muon_charge[isProbe]')

    df = df.Define('tag_Eta','Muon_eta[isTag]')
    # Filter on pairs of lepton with DeltaR > 0.4 and 80 < mll < 100

    filterstr = '''
    for (unsigned int line = 0; line < dr_mll.size(); line++){
    for (unsigned int col = 0; col < 2; col++){
    '''+\
    '''
    float DeltaR = dr_mll[line][col][0];
    float mll = dr_mll[line][col][1];
    if (DeltaR > 0.4 && mll > {} && mll < {})'''.format(massmin, massmax)+\
    '''{
    return true;
    }
    }
    }
    return false;
    '''
    df = df.Filter(filterstr)

    df = df.Define('barrelbarrel','abs(Muon_eta[0])<1.24&&abs(Muon_eta[1])<1.24')
    df = df.Define('endcapendcap','abs(Muon_eta[0])>1.24&&abs(Muon_eta[1])>1.24')
    return df

def DiJetSelection(df):
    '''
    Select events with two jets with pt>500 GeV and mjj>1000 GeV
    The event must pass a jet trigger. 
    '''

    df = df.Filter('HLT_AK8PFJet500&&PuppiMET_pt<300')
    #df = df.Define('isHighPtJet','Jet_jetId>=6&&Jet_pt>500&&Jet_muEF<0.5&&Jet_chEmEF<0.5&&Jet_neEmEF<0.8')
    df = df.Define('isHighPtJet', 'passPFJetID && Jet_pt > 500 && Jet_muEF < 0.5 && Jet_chEmEF < 0.5 && Jet_neEmEF < 0.8')

    df = df.Filter('Sum(isHighPtJet)==2','=2 jets with pt>500 GeV')
    df = df.Filter('isHighPtJet[0]&&isHighPtJet[1]','First 2 jets are the cleaned jets')
    df = df.Define('highPtJet_Pt','Jet_pt[isHighPtJet]')
    df = df.Define('highPtJet_Eta','Jet_eta[isHighPtJet]')
    df = df.Define('highPtJet_Phi','Jet_phi[isHighPtJet]')
    
    
    df = df.Define('_mjj', 'mll(Jet_pt, Jet_eta, Jet_phi, isHighPtJet, isHighPtJet)')
    df = df.Filter('_mjj>1000')

    df = df.Define('barrelbarrel','abs(highPtJet_Eta[0])<1.3&&abs(highPtJet_Eta[1])<1.3')
    df = df.Define('endcapendcap','abs(highPtJet_Eta[0])>1.3&&abs(highPtJet_Eta[1])>1.3')
    
    
    return df

def ZTauTauSelection(df):
    '''
    Selects Z->tautau events passing a single muon trigger. Defines probe tau pt/eta/phi
    The selections are made to match with DQM Off selections
    '''
    df = df.Filter('HLT_IsoMu24||HLT_IsoMu27','HLT_IsoMu24||HLT_IsoMu27')

    # Trigged on a Muon (probably redundant)
    df = df.Filter('''
    bool trigged_on_mu = false;
    for (unsigned int i = 0; i < TrigObj_id.size(); i++){
        if(TrigObj_id[i] == 13) trigged_on_mu = true;
    }
    return trigged_on_mu;
    ''','trigger on muon')

    # TrigObj matching
    df = df.Define('Muon_trig_idx', 'MatchObjToTrig(Muon_eta, Muon_phi, TrigObj_pt, TrigObj_eta, TrigObj_phi, TrigObj_id, 13, TrigObj_filterBits, 3, 0.6)')
    df = df.Define('Muon_passHLT_IsoMu24', 'trig_is_filterbit1_set(Muon_trig_idx, TrigObj_filterBits, 3)')

    # Tag Muon Selection
    df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId') 
    df = df.Define('Muon_MassId', 'pass_muon_met_mass_belowX(Muon_pt, Muon_phi, PuppiMET_pt, PuppiMET_phi,40)')
    df = df.Define('isTag','Muon_pt>24&&abs(Muon_eta)<2.4&&abs(Muon_pdgId)==13&&Muon_PassTightId&&Muon_passHLT_IsoMu24&&Muon_MassId')
    df = df.Filter('Sum(isTag)==1', 'found a tag')
    df = df.Define('tagIdx', 'first_tagmuon_idx(isTag)')
    df = df.Filter('tagIdx!=-1','tagIdx!=-1')

    df = df.Define('tagPt', 'Muon_pt[tagIdx]')
    df = df.Define('tagEta', 'Muon_eta[tagIdx]')
    df = df.Define('tagPhi', 'Muon_phi[tagIdx]')
    df = df.Define('tagMass', 'Muon_mass[tagIdx]')
    df = df.Define('tagCharge', 'Muon_charge[tagIdx]')

    # Decay mode 5 and 6 are unphysical, so removing them
    # Applying Tau_Id_Discrimination against e, mu, jets
    # Applying probe tau selection criterion with the given tag muon
    df = df.Define('Tau_PassDecayMode', 'Tau_decayMode!=5&&Tau_decayMode!=6')
    df = df.Define('Tau_PassTightId', 'Tau_idDeepTau2018v2p5VSe>=1&&Tau_idDeepTau2018v2p5VSjet>=2&&Tau_idDeepTau2018v2p5VSmu>=1')
    df = df.Define('Tau_PassProbe', 'pass_probeTau(Tau_pt, Tau_eta, Tau_phi, Tau_mass, Tau_charge, tagPt, tagEta, tagPhi, tagMass, tagCharge)')
    df = df.Define('isProbeTau', 'Tau_PassDecayMode&&Tau_PassTightId&&Tau_PassProbe')
    df = df.Filter('Sum(isProbeTau)==1','=1 probe tau')

    df = df.Define('probe_Pt','Tau_pt[isProbeTau]')
    df = df.Define('probe_Eta','Tau_eta[isProbeTau]')
    df = df.Define('probe_Phi','Tau_phi[isProbeTau]')

    return df



def makehistosforturnons_inprobeetaranges(df, histos, etavarname, phivarname, ptvarname, responsevarname, l1varname, l1thresholds, prefix, binning, l1thresholdforeffvsrunnb, offlinethresholdforeffvsrunnb, suffix = ''):
    '''Make histos for turnons vs pt (1D histos for numerator and denominator) in ranges of eta
    Also look at response vs run number (2D histo) '''

    for (i, r) in enumerate(config["Regions"]):
        region = config["Regions"][r]

        # check that runnb_bins are set
        if runnb_bins is None:
            set_runnbbins(df)

        str_bineta = "eta{}to{}".format(region[0], region[1]).replace(".","p")
        #Define columns corresponding to pt and response for the selected eta range 
        df_etarange = df.Define('inEtaRange','abs({})>={}'.format(etavarname, region[0])+'&&abs({})<{}'.format(etavarname, region[1]))
        df_etarange = df_etarange.Filter('PuppiMET_pt<100')
        df_etarange = df_etarange.Define('denominator_pt',ptvarname+'[inEtaRange]')
        df_etarange = df_etarange.Define('response',responsevarname+'[inEtaRange]')
        df_etarange = df_etarange.Define('runnb',"return ROOT::VecOps::RVec<int>(response.size(), run);")
        histos[prefix+str_bineta+suffix] = df_etarange.Histo1D(ROOT.RDF.TH1DModel('h_{}_{}'.format(prefix, str_bineta)+suffix, '', len(binning)-1, binning), 'denominator_pt')

        if config["Response"]:
            #Response vs pt and vs runnb (2d)
            histos[prefix+str_bineta+'_ResponseVsPt'+suffix] = df_etarange.Histo2D(ROOT.RDF.TH2DModel('h_ResponseVsPt_{}_{}'.format(prefix, str_bineta)+suffix, '', 200, 0, 200, 100, 0, 2), 'denominator_pt', 'response')
            histos[prefix+str_bineta+'_ResponseVsPt_big_bins'+suffix] = df_etarange.Histo2D(ROOT.RDF.TH2DModel('h_ResponseVsPt_big_bins_{}_{}'.format(prefix, str_bineta)+suffix, '', 20, 0, 200, 100, 0, 2), 'denominator_pt', 'response')
            histos[prefix+str_bineta+'_ResponseVsRunNb'+suffix] = df_etarange.Histo2D(ROOT.RDF.TH2DModel('h_ResponseVsRunNb_{}_{}'.format(prefix, str_bineta)+suffix, '', len(runnb_bins)-1, runnb_bins, len(response_bins)-1, response_bins), 'runnb', 'response')

        #if i ==1 and prefix == 'EGNonIso_plots':
        #    df_etarange = df_etarange.Filter(stringToPrint)

        if config["Efficiency"]:
            #Numerator/denominator for plateau eff vs runnb
            df_etarange = df_etarange.Define('inplateau','{}>={}&&inEtaRange'.format(ptvarname,offlinethresholdforeffvsrunnb))
            df_etarange = df_etarange.Define('N_inplateau','Sum(inplateau)')
            df_etarange = df_etarange.Define('runnb_inplateau',"return ROOT::VecOps::RVec<int>(N_inplateau, run);")
            df_etarange = df_etarange.Define('inplateaupassL1','inplateau && {}>={}'.format(l1varname,l1thresholdforeffvsrunnb))
            df_etarange = df_etarange.Define('N_inplateaupassL1','Sum(inplateaupassL1)')
            df_etarange = df_etarange.Define('runnb_inplateaupassL1',"return ROOT::VecOps::RVec<int>(N_inplateaupassL1, run);")
            histos[prefix+"_plateaueffvsrunnb_numerator_"+str_bineta+suffix] = df_etarange.Histo1D(ROOT.RDF.TH1DModel('h_PlateauEffVsRunNb_Numerator_{}_{}'.format(prefix, str_bineta)+suffix, '', len(runnb_bins)-1, runnb_bins),'runnb_inplateaupassL1')
            histos[prefix+"_plateaueffvsrunnb_denominator_"+str_bineta+suffix] = df_etarange.Histo1D(ROOT.RDF.TH1DModel('h_PlateauEffVsRunNb_Denominator_{}_{}'.format(prefix, str_bineta)+suffix, '', len(runnb_bins)-1, runnb_bins),'runnb_inplateau')

        if config["TurnOns"]:
            for ipt in l1thresholds:
                str_binetapt = "eta{}to{}_l1thrgeq{}".format(region[0], region[1], ipt).replace(".","p")
                df_loc = df_etarange.Define('passL1Cond','{}>={}'.format(l1varname, ipt))
                df_loc = df_loc.Define('numerator_pt',ptvarname+'[inEtaRange&&passL1Cond]')
                histos[prefix+str_binetapt+suffix] = df_loc.Histo1D(ROOT.RDF.TH1DModel('h_{}_{}'.format(prefix, str_binetapt)+suffix, '', len(binning)-1, binning), 'numerator_pt')


    return df

def ZEE_Plots(df, suffix = ''):
    histos = {}
    
    df_eg = [None] * len(config['Isos'])

    for i, iso in enumerate(config['Isos']):
        
        df_eg[i] = df.Define('probe_idxL1EG','FindL1ObjIdx(L1EG_eta, L1EG_phi, probe_Eta, probe_Phi, L1EG_hwIso, {})'.format(config['Isos'][iso]))
        df_eg[i] = df_eg[i].Define('probe_idxL1EG_Bx0','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, probe_Eta, probe_Phi, 0, L1EG_hwIso, {})'.format(config['Isos'][iso]))
        df_eg[i] = df_eg[i].Define('probe_idxL1EG_Bxmin1','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, probe_Eta, probe_Phi, -1, L1EG_hwIso, {})'.format(config['Isos'][iso]))
        df_eg[i] = df_eg[i].Define('probe_idxL1EG_Bxplus1','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, probe_Eta, probe_Phi, 1, L1EG_hwIso, {})'.format(config['Isos'][iso]))

        df_eg[i] = df_eg[i].Define('probe_L1EG_Pt','GetVal(probe_idxL1EG, L1EG_pt)')
        df_eg[i] = df_eg[i].Define('probe_L1EG_Bx','GetVal(probe_idxL1EG, L1EG_bx)')
        df_eg[i] = df_eg[i].Define('probe_L1EG_PtoverRecoPt','probe_L1EG_Pt/probe_Pt')

        pt_binning = leptonpt_bins
        if suffix != '':
            pt_binning = coarse_leptonpt_bins
        
        df_eg[i] = makehistosforturnons_inprobeetaranges(df_eg[i], histos, etavarname='probe_Eta', phivarname='probe_Phi', ptvarname='probe_Pt', responsevarname='probe_L1EG_PtoverRecoPt',  l1varname='probe_L1EG_Pt', l1thresholds=config["Thresholds"], prefix=iso+"_plots", binning=pt_binning, l1thresholdforeffvsrunnb = 30, offlinethresholdforeffvsrunnb = 35, suffix = suffix)
        
        if config['Efficiency']: 
            df_eg[i] = df_eg[i].Define('probePt30_Eta','probe_Eta[probe_Pt>30]')
            df_eg[i] = df_eg[i].Define('probePt30_Phi','probe_Phi[probe_Pt>30]')
            df_eg[i] = df_eg[i].Define('probePt30PassL1EG25_Eta','probe_Eta[probe_Pt>30&&probe_L1EG_Pt>25]')
            df_eg[i] = df_eg[i].Define('probePt30PassL1EG25_Phi','probe_Phi[probe_Pt>30&&probe_L1EG_Pt>25]')
            histos['h_EG25_EtaPhi_Numerator'+iso+suffix] = df_eg[i].Histo2D(ROOT.RDF.TH2DModel('h_EG25_EtaPhi_Numerator'+iso+suffix, '', 100, -5,5, 100, -3.1416, 3.1416), 'probePt30PassL1EG25_Eta', 'probePt30PassL1EG25_Phi')
            histos['h_EG25_EtaPhi_Denominator'+iso+suffix] = df_eg[i].Histo2D(ROOT.RDF.TH2DModel('h_EG25_EtaPhi_Denominator'+iso+suffix, '', 100, -5,5, 100, -3.1416, 3.1416), 'probePt30_Eta', 'probePt30_Phi')

        
        if iso == 'EGNonIso' and config['Prefiring']:
            for bx in ['min1', '0', 'plus1'] :
                df_eg[i] = df_eg[i].Define('probe_L1EG_Pt_Bx{}'.format(bx), 'GetVal(probe_idxL1EG_Bx{}, L1EG_pt)'.format(bx))
                
            histos = getprefiringhistos(df_eg[i], histos, probecondition='probe_Pt>25', l1objname='L1EG', etabinning=[-2.5, -1.479, 0., 1.479, 2.5], ptbinning=coarse_leptonpt_bins, l1threshold=20, suffix=suffix)

            
    return df, histos




def ZEE_Forward_Plots(df, suffix = ''):
    histos = {}
    
    histos['mll_Forward2p5to2p7_zoom'] =  df.Filter('abs(probe_Eta[0])>2.5&&abs(probe_Eta[0])<2.7').Histo1D(ROOT.RDF.TH1DModel('mll_Forward2p5to2p7_zoom', '', 60, 60, 120 ), '_mll') 
    histos['mll_Forward2p7to3p0_zoom'] =  df.Filter('abs(probe_Eta[0])>2.7').Histo1D(ROOT.RDF.TH1DModel('mll_Forward2p7to3p0_zoom', '', 60, 60, 120 ), '_mll') 
    
    df_eg = df.Define('probe_idxL1EG','FindL1ObjIdx(L1EG_eta, L1EG_phi, probe_Eta, probe_Phi, L1EG_hwIso,-1)')
    df_eg = df_eg.Define('probe_idxL1EG_Bx0','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, probe_Eta, probe_Phi, 0, L1EG_hwIso,-1)')
    df_eg = df_eg.Define('probe_idxL1EG_Bxmin1','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, probe_Eta, probe_Phi, -1, L1EG_hwIso,-1)')
    df_eg = df_eg.Define('probe_idxL1EG_Bxplus1','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, probe_Eta, probe_Phi, 1, L1EG_hwIso,-1)')
    
    df_eg = df_eg.Define('probe_L1EG_Pt','GetVal(probe_idxL1EG, L1EG_pt)')
    df_eg = df_eg.Define('probe_L1EG_Bx','GetVal(probe_idxL1EG, L1EG_bx)')
    df_eg = df_eg.Define('probe_L1EG_PtoverRecoPt','probe_L1EG_Pt/probe_Pt')

    for bx in ['min1', '0', 'plus1'] :
        df_eg = df_eg.Define('probe_L1EG_Pt_Bx{}'.format(bx), 'GetVal(probe_idxL1EG_Bx{}, L1EG_pt)'.format(bx))

    histos = getprefiringhistos(df_eg, histos, probecondition='probe_Pt>25', l1objname='L1EG', etabinning=[-3, -2.5, 2.5, 3.], ptbinning=coarse_leptonpt_bins, l1threshold=20, suffix='_fwd'+suffix)
    
    return df, histos


    
def ZMuMu_Plots(df, suffix = ''):

    histos = {}
    df_mu = [None] * len(config["Qualities"])

    for i, qual in enumerate(config["Qualities"]):

        df_mu[i] = df.Define('probe_idxL1Mu','FindL1MuIdx(L1Mu_eta, L1Mu_phi, probe_Eta, probe_Phi, probe_Pt, probe_Charge, L1Mu_hwQual, {})'.format(config["Qualities"][qual]))
        df_mu[i] = df_mu[i].Define('probe_idxL1Mu_Bx0','FindL1MuIdx_setBx(L1Mu_eta, L1Mu_phi, L1Mu_bx, probe_Eta, probe_Phi, probe_Pt, probe_Charge, 0, L1Mu_hwQual, {})'.format(config["Qualities"][qual]))
        df_mu[i] = df_mu[i].Define('probe_idxL1Mu_Bxmin1','FindL1MuIdx_setBx(L1Mu_eta, L1Mu_phi, L1Mu_bx, probe_Eta, probe_Phi, probe_Pt, probe_Charge, -1, L1Mu_hwQual, {})'.format(config["Qualities"][qual]))
        df_mu[i] = df_mu[i].Define('probe_idxL1Mu_Bxplus1','FindL1MuIdx_setBx(L1Mu_eta, L1Mu_phi, L1Mu_bx, probe_Eta, probe_Phi, probe_Pt, probe_Charge, 1, L1Mu_hwQual, {})'.format(config["Qualities"][qual]))
        
        df_mu[i] = df_mu[i].Define('probe_L1Mu_Pt','GetVal(probe_idxL1Mu, L1Mu_pt)')
        df_mu[i] = df_mu[i].Define('probe_L1Mu_Bx','GetVal(probe_idxL1Mu, L1Mu_bx)')
        df_mu[i] = df_mu[i].Define('probe_L1Mu_Qual','GetVal(probe_idxL1Mu, L1Mu_hwQual)')

        
        
        df_mu[i] = df_mu[i].Define('probe_L1Mu_PtoverRecoPt','probe_L1Mu_Pt/probe_Pt')

        pt_binning = leptonpt_bins
        if suffix != '':
            pt_binning = coarse_leptonpt_bins

        df_mu[i] = makehistosforturnons_inprobeetaranges(df_mu[i], histos, etavarname='probe_Eta', phivarname='probe_Phi', ptvarname='probe_Pt', responsevarname='probe_L1Mu_PtoverRecoPt', l1varname='probe_L1Mu_Pt', l1thresholds=config["Thresholds"],  prefix=qual+"_plots" , binning = pt_binning, l1thresholdforeffvsrunnb = 22, offlinethresholdforeffvsrunnb = 27, suffix = suffix)
                
        if config["Efficiency"]:
            df_mu[i] = df_mu[i].Define('probePt30_Eta','probe_Eta[probe_Pt>30]')
            df_mu[i] = df_mu[i].Define('probePt30_Phi','probe_Phi[probe_Pt>30]')
            df_mu[i] = df_mu[i].Define('probePt30PassL1Mu22_Eta','probe_Eta[probe_Pt>30&&probe_L1Mu_Pt>22]')
            df_mu[i] = df_mu[i].Define('probePt30PassL1Mu22_Phi','probe_Phi[probe_Pt>30&&probe_L1Mu_Pt>22]')
        
            histos['h_Mu22_EtaPhi_Denominator'+qual+suffix] = df_mu[i].Histo2D(ROOT.RDF.TH2DModel('h_Mu22_EtaPhi_Denominator'+qual+suffix, '', 100, -5,5, 100, -3.1416, 3.1416), 'probePt30_Eta', 'probePt30_Phi')
            histos['h_Mu22_EtaPhi_Numerator'+qual+suffix] = df_mu[i].Histo2D(ROOT.RDF.TH2DModel('h_Mu22_EtaPhi_Numerator'+qual+suffix, '', 100, -5,5, 100, -3.1416, 3.1416), 'probePt30PassL1Mu22_Eta', 'probePt30PassL1Mu22_Phi')
        


        if qual == "Qual12" and config["Prefiring"]:
            for bx in ['min1', '0', 'plus1'] :
                df_mu[i] = df_mu[i].Define('probe_L1Mu_Pt_Bx{}'.format(bx), 'GetVal(probe_idxL1Mu_Bx{}, L1Mu_pt)'.format(bx))
        
            histos = getprefiringhistos(df_mu[i], histos, probecondition='probe_Pt>20', l1objname='L1Mu', etabinning=[-2.4,-1.24,-0.83,0.,0.83,1.24,2.4], ptbinning=coarse_leptonpt_bins, l1threshold=10, suffix=suffix)

        
    return df, histos




def ZTauTau_Plots(df, suffix = ''):
    histos = {}
    
    df_tau = [None] * len(config['Isos'])

    for i, iso in enumerate(config['Isos']):
        
        df_tau[i] = df.Define('probe_idxL1Tau','FindL1ObjIdx(L1Tau_eta, L1Tau_phi, probe_Eta, probe_Phi, L1Tau_hwIso, {})'.format(config['Isos'][iso]))
        df_tau[i] = df_tau[i].Define('probe_idxL1Tau_Bx0','FindL1ObjIdx_setBx(L1Tau_eta, L1Tau_phi, L1Tau_bx, probe_Eta, probe_Phi, 0, L1Tau_hwIso, {})'.format(config['Isos'][iso]))
        df_tau[i] = df_tau[i].Define('probe_idxL1Tau_Bxmin1','FindL1ObjIdx_setBx(L1Tau_eta, L1Tau_phi, L1Tau_bx, probe_Eta, probe_Phi, -1, L1Tau_hwIso, {})'.format(config['Isos'][iso]))
        df_tau[i] = df_tau[i].Define('probe_idxL1Tau_Bxplus1','FindL1ObjIdx_setBx(L1Tau_eta, L1Tau_phi, L1Tau_bx, probe_Eta, probe_Phi, 1, L1Tau_hwIso, {})'.format(config['Isos'][iso]))

        df_tau[i] = df_tau[i].Define('probe_L1Tau_Pt','GetVal(probe_idxL1Tau, L1Tau_pt)')
        df_tau[i] = df_tau[i].Define('probe_L1Tau_Bx','GetVal(probe_idxL1Tau, L1Tau_bx)')
        df_tau[i] = df_tau[i].Define('probe_L1Tau_PtoverRecoPt','probe_L1Tau_Pt/probe_Pt')

        pt_binning = leptonpt_bins
        if suffix != '':
            pt_binning = coarse_leptonpt_bins
        
        df_tau[i] = makehistosforturnons_inprobeetaranges(df_tau[i], histos, etavarname='probe_Eta', phivarname='probe_Phi', ptvarname='probe_Pt', responsevarname='probe_L1Tau_PtoverRecoPt',  l1varname='probe_L1Tau_Pt', l1thresholds=config["Thresholds"], prefix=iso+"_plots", binning=pt_binning, l1thresholdforeffvsrunnb = 30, offlinethresholdforeffvsrunnb = 40, suffix = suffix)
        
        if config['Efficiency']: 
            df_tau[i] = df_tau[i].Define('probePt40_Eta','probe_Eta[probe_Pt>40]')
            df_tau[i] = df_tau[i].Define('probePt40_Phi','probe_Phi[probe_Pt>40]')
            df_tau[i] = df_tau[i].Define('probePt40PassL1Tau30_Eta','probe_Eta[probe_Pt>40&&probe_L1Tau_Pt>30]')
            df_tau[i] = df_tau[i].Define('probePt40PassL1Tau30_Phi','probe_Phi[probe_Pt>40&&probe_L1Tau_Pt>30]')
            histos['h_Tau30_EtaPhi_Numerator'+iso+suffix] = df_tau[i].Histo2D(ROOT.RDF.TH2DModel('h_Tau30_EtaPhi_Numerator'+iso+suffix, '', 100, -5,5, 100, -3.1416, 3.1416), 'probePt40PassL1Tau30_Eta', 'probePt40PassL1Tau30_Phi')
            histos['h_Tau30_EtaPhi_Denominator'+iso+suffix] = df_tau[i].Histo2D(ROOT.RDF.TH2DModel('h_Tau30_EtaPhi_Denominator'+iso+suffix, '', 100, -5,5, 100, -3.1416, 3.1416), 'probePt40_Eta', 'probePt40_Phi')

        
            
    return df, histos






def L1ETMHF(df):
    
    df = df.Define('L1EtSum_isETMHF','L1EtSum_etSumType==8&&L1EtSum_bx==0')
    df = df.Define('L1ETMHF_array','L1EtSum_pt[L1EtSum_isETMHF]')
    df = df.Define('L1ETMHF_phi_array','L1EtSum_phi[L1EtSum_isETMHF]')
    df = df.Define('L1ETMHF','L1ETMHF_array[0]')
    df = df.Define('L1ETMHF_phi','L1ETMHF_phi_array[0]')

    df = df.Define('L1EtSum_bxmin1_isETMHF','L1EtSum_etSumType==8&&L1EtSum_bx==-1')
    df = df.Define('L1ETMHF_bxmin1_array','L1EtSum_pt[L1EtSum_bxmin1_isETMHF]')
    df = df.Define('L1ETMHF_bxmin1_phi_array','L1EtSum_phi[L1EtSum_bxmin1_isETMHF]')
    df = df.Define('L1ETMHF_bxmin1','L1ETMHF_bxmin1_array[0]')
    df = df.Define('L1ETMHF_bxmin1_phi','L1ETMHF_bxmin1_phi_array[0]')

    df = df.Define('L1EtSum_bxplus1_isETMHF','L1EtSum_etSumType==8&&L1EtSum_bx==-1')
    df = df.Define('L1ETMHF_bxplus1_array','L1EtSum_pt[L1EtSum_bxplus1_isETMHF]')
    df = df.Define('L1ETMHF_bxplus1_phi_array','L1EtSum_phi[L1EtSum_bxplus1_isETMHF]')
    df = df.Define('L1ETMHF_bxplus1','L1ETMHF_bxplus1_array[0]')
    df = df.Define('L1ETMHF_bxplus1_phi','L1ETMHF_bxplus1_phi_array[0]')
    
    return df

def PassPFJetID(df):
    # Jet ID based on energy fractions and multiplicities
    df = df.Define("absJetEta", "abs(Jet_eta)")
    df = df.Define("passPFJetID",
        """
        (absJetEta <= 2.6 && Jet_neHEF < 0.90 && Jet_neEmEF < 0.90 && Jet_nConstituents > 1 &&
        Jet_muEF < 0.80 && Jet_chHEF > 0.01 && Jet_chMultiplicity > 0 && Jet_chEmEF < 0.80) ||

        (absJetEta > 2.6 && absJetEta <= 2.7 && Jet_neHEF < 0.90 && Jet_neEmEF < 0.99 &&
        Jet_muEF < 0.80 && Jet_chEmEF < 0.80) ||

        (absJetEta > 2.7 && absJetEta <= 3.0 && Jet_neHEF < 0.9999) ||
    
        (absJetEta > 3.0 && absJetEta <= 5.0 && Jet_neEmEF < 0.90 && Jet_neMultiplicity > 2)
        """
    )

    return df

def CleanJets(df):
    #List of cleaned jets (noise cleaning + lepton/photon overlap removal)
    #df = df.Define('_jetPassID', 'Jet_jetId>=4')
    #df = df.Define('isCleanJet','_jetPassID&&Jet_pt>30&&Jet_muEF<0.5&&Jet_chEmEF<0.5')
    df = df.Define('isCleanJet', 'passPFJetID && Jet_pt > 30 && Jet_muEF < 0.5 && Jet_chEmEF < 0.5')
    df = df.Define('cleanJet_Pt','Jet_pt[isCleanJet]')
    df = df.Define('cleanJet_Eta','Jet_eta[isCleanJet]')
    df = df.Define('cleanJet_Phi','Jet_phi[isCleanJet]')
    df = df.Define('cleanJet_NHEF','Jet_neHEF[isCleanJet]')
    df = df.Define('cleanJet_NEEF','Jet_neEmEF[isCleanJet]')
    df = df.Define('cleanJet_CHEF','Jet_chHEF[isCleanJet]')
    df = df.Define('cleanJet_CEEF','Jet_chEmEF[isCleanJet]')
    df = df.Define('cleanJet_MUEF','Jet_muEF[isCleanJet]')
    df = df.Filter(stringToPrintJets)
    df = df.Filter('Sum(isCleanJet)>=1','>=1 clean jet with p_{T}>30 GeV')
    
    return df

def lepton_ismuon(df):
    df = df.Define('_lPt', 'Muon_pt')
    df = df.Define('_lEta', 'Muon_eta')
    df = df.Define('_lPhi', 'Muon_phi')
    df = df.Define('_lpdgId', 'Muon_pdgId')
    return(df)

def lepton_iselectron(df):
    df = df.Define('_lPt', 'Electron_pt')
    df = df.Define('_lEta', 'Electron_eta')
    df = df.Define('_lPhi', 'Electron_phi')
    df = df.Define('_lpdgId', 'Electron_pdgId')
    return(df)

def EtSum(df, suffix = ''):
    histos = {}

    #HT=scalar pt sum of all jets with pt>30 and |eta|<2.5 
    df = df.Define('iscentraljet','cleanJet_Pt>30&&abs(cleanJet_Eta)<2.5')
    #df = df.Filter('Sum(iscentraljet)>0')
    df = df.Define('HT','Sum(cleanJet_Pt[cleanJet_Pt>30&&abs(cleanJet_Eta)<2.5])')

    df = df.Define('muons_px','Sum(_lPt[abs(_lpdgId)==13]*cos(_lPhi[abs(_lpdgId)==13]))')
    df = df.Define('muons_py','Sum(_lPt[abs(_lpdgId)==13]*sin(_lPhi[abs(_lpdgId)==13]))')
    df = df.Define('metnomu_x','PuppiMET_pt*cos(PuppiMET_phi)+muons_px')
    df = df.Define('metnomu_y','PuppiMET_pt*sin(PuppiMET_phi)+muons_py')
    df = df.Define('MetNoMu','sqrt(metnomu_x*metnomu_x+metnomu_y*metnomu_y)')

    # Dijet selections

    df = df.Define('hastwocleanjets', 'PassDiJet(cleanJet_Pt, cleanJet_Eta, cleanJet_Phi, 80, 40, 500)')
    df = df.Define('vbf_selection', 'PassDiJet(cleanJet_Pt, cleanJet_Eta, cleanJet_Phi, 140, 70, 900)')

    df = df.Define('hastwocentraljets', 'PassDiJet80_40_Mjj500_central(cleanJet_Pt, cleanJet_Eta, cleanJet_Phi)')
    df = df.Define('hastwoHFjets', 'PassDiJet80_40_Mjj500_HF(cleanJet_Pt, cleanJet_Eta, cleanJet_Phi)')
    df = df.Define('HLT_VBF_filter', 'PassDiJet75_40_500(cleanJet_Pt, cleanJet_Eta, cleanJet_Phi)')

    histos['h_MetNoMu_Denominator'+suffix] = df.Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_Denominator'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu') 
    
    dfmetl1 = df.Filter('L1_ETMHF80')
    histos['L1_ETMHF80'+suffix] = dfmetl1.Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_ETMHF80'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
    dfmetl1 = df.Filter('L1_ETMHF90')
    histos['L1_ETMHF90'+suffix] = dfmetl1.Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_ETMHF90'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
    dfmetl1 = df.Filter('L1_ETMHF100')
    histos['L1_ETMHF100'+suffix] = dfmetl1.Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_ETMHF100'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
    dfmetl1 = df.Filter('L1_ETMHF110')
    histos['L1_ETMHF110'+suffix] = dfmetl1.Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_ETMHF110'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')

    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight'+suffix] =  df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60'+suffix] =  df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
    

    histos['h_HT_Denominator'+suffix] = df.Filter('PuppiMET_pt<50').Histo1D(ROOT.RDF.TH1DModel('h_HT_Denominator'+suffix, '', len(ht_bins)-1, array('d',ht_bins)), 'HT') 
    histos['L1_HTT200er'+suffix] = df.Filter('L1_HTT200er').Filter('PuppiMET_pt<50').Histo1D(ROOT.RDF.TH1DModel('h_HT_L1_HTT200er'+suffix, '', len(ht_bins)-1, array('d',ht_bins)), 'HT')  
    histos['L1_HTT280er'+suffix] = df.Filter('L1_HTT280er').Filter('PuppiMET_pt<50').Histo1D(ROOT.RDF.TH1DModel('h_HT_L1_HTT280er'+suffix, '', len(ht_bins)-1, array('d',ht_bins)), 'HT')
    histos['L1_HTT360er'+suffix] = df.Filter('L1_HTT360er').Filter('PuppiMET_pt<50').Histo1D(ROOT.RDF.TH1DModel('h_HT_L1_HTT360er'+suffix, '', len(ht_bins)-1, array('d',ht_bins)), 'HT')
    histos['HLT_PFHT1050'+suffix] =  df.Filter('HLT_PFHT1050').Filter('PuppiMET_pt<50').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFHT1050'+suffix, '', len(ht_bins)-1, array('d',ht_bins)), 'HT')

    # DiJet selections:

    # DiJet 80 40
    histos['h_MetNoMu_Denominator_DiJet80_40_Mjj500'+suffix] = df.Filter('hastwocleanjets').Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_Denominator_DiJet80_40_Mjj500'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu') 
    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet80_40_Mjj500'+suffix] = df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight&&hastwocleanjets').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet80_40_Mjj500'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60_DiJet80_40_Mjj500'+suffix] = df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60&&hastwocleanjets').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60_DiJet80_40_Mjj500'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')

    # central dijet
    histos['h_MetNoMu_Denominator_DiJet80_40_Mjj500_central'+suffix] = df.Filter('hastwocentraljets').Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_Denominator_DiJet80_40_Mjj500_central'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu') 
    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet80_40_Mjj500_central'+suffix] = df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight&&hastwocentraljets').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet80_40_Mjj500_central'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')

    # HF dijets
    histos['h_MetNoMu_Denominator_DiJet80_40_Mjj500_HF'+suffix] = df.Filter('hastwoHFjets').Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_Denominator_DiJet80_40_Mjj500_HF'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu') 
    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet80_40_Mjj500_HF'+suffix] = df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight&&hastwoHFjets').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet80_40_Mjj500_HF'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')

    # VBF selection (DiJet 140 70, mjj > 900 GeV) denominator
    histos['h_MetNoMu_Denominator_DiJet140_70_Mjj900'+suffix] = df.Filter('vbf_selection').Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_Denominator_DiJet140_70_Mjj900'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu') 

    # Normal (MET only) trigger
    histos['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet140_70_Mjj900'+suffix] = df.Filter('HLT_PFMETNoMu120_PFMHTNoMu120_IDTight&&vbf_selection').Histo1D(ROOT.RDF.TH1DModel('h_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_DiJet140_70_Mjj900'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')

    ## VBF (Met + jet) trigger
    # histos['HLT_DiJet110_35_Mjj650_PFMET110_DiJet140_70_Mjj900'+suffix] =  df.Filter('HLT_DiJet110_35_Mjj650_PFMET110&&vbf_selection').Histo1D(ROOT.RDF.TH1DModel('h_HLT_DiJet110_35_Mjj650_PFMET110_DiJet140_70_Mjj900'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')

    # VBF trigger
    if max(runnb_bins) > 367661:
        histos['h_MetNoMu_Denominator_VBF_DiJet70_40_500'+suffix] = df.Filter('run>367661').Filter('HLT_VBF_filter').Histo1D(ROOT.RDF.TH1DModel('h_MetNoMu_Denominator_VBF_DiJet70_40_500'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
        histos['HLT_VBF_DiPFJet75_40_Mjj500_Detajj2p5_PFMET85'+suffix] =  df.Filter('run>367661').Filter('HLT_VBF_filter&&HLT_VBF_DiPFJet75_40_Mjj500_Detajj2p5_PFMET85').Histo1D(ROOT.RDF.TH1DModel('HLT_VBF_DiPFJet75_40_Mjj500_Detajj2p5_PFMET85'+suffix, '', len(jetmetpt_bins)-1, array('d',jetmetpt_bins)), 'MetNoMu')
        
    return df, histos

def AnalyzeCleanJets(df, JetRecoPtCut, L1JetPtCut, suffix = ''):    
    histos = {}
    #Find L1 jets matched to the offline jet

    df = df.Define('cleanJet_idxL1jetbx0', 'FindL1ObjIdx_setBx(L1Jet_eta, L1Jet_phi, L1Jet_bx, cleanJet_Eta, cleanJet_Phi, 0)')
    df = df.Define('cleanJet_idxL1jetbxmin1', 'FindL1ObjIdx_setBx(L1Jet_eta, L1Jet_phi, L1Jet_bx, cleanJet_Eta, cleanJet_Phi, -1)')
    df = df.Define('cleanJet_idxL1jetbx1', 'FindL1ObjIdx_setBx(L1Jet_eta, L1Jet_phi, L1Jet_bx, cleanJet_Eta, cleanJet_Phi, 1)')

    df = df.Define('cleanJet_L1Pt','GetVal(cleanJet_idxL1jetbx0,L1Jet_pt)')
    df = df.Define('cleanJet_L1Ptbxmin1','GetVal(cleanJet_idxL1jetbxmin1,L1Jet_pt)')
    df = df.Define('cleanJet_L1Ptbx1','GetVal(cleanJet_idxL1jetbx1,L1Jet_pt)')
    
    df = df.Define('cleanJet_L1PtoverRecoPt','cleanJet_L1Pt/cleanJet_Pt')

    df = df.Define('cleanJet_idxL1egbx0', 'FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, cleanJet_Eta, cleanJet_Phi, 0)')
    df = df.Define('cleanJet_idxL1egbxmin1', 'FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, cleanJet_Eta, cleanJet_Phi, -1)')
    df = df.Define('cleanJet_idxL1egbx1', 'FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, cleanJet_Eta, cleanJet_Phi, 1)')

    df = df.Define('cleanJet_L1EGPt','GetVal(cleanJet_idxL1egbx0,L1EG_pt)')
    df = df.Define('cleanJet_L1EGPtbxmin1','GetVal(cleanJet_idxL1egbxmin1,L1EG_pt)')
    df = df.Define('cleanJet_L1EGPtbx1','GetVal(cleanJet_idxL1egbx1,L1EG_pt)')

    #df = df.Filter(stringFailingJets)
    #Now some plotting (turn ons for now)
    L1PtCuts = [30., 40., 60., 80., 100., 120., 140., 160., 170., 180., 200.]


    df = makehistosforturnons_inprobeetaranges(df, histos, etavarname='cleanJet_Eta', phivarname='cleanJet_Phi', ptvarname='cleanJet_Pt', responsevarname='cleanJet_L1PtoverRecoPt', l1varname='cleanJet_L1Pt', l1thresholds=config['Thresholds'], prefix="Jet_plots", binning=jetmetpt_bins, l1thresholdforeffvsrunnb = L1JetPtCut, offlinethresholdforeffvsrunnb = JetRecoPtCut, suffix = suffix) 
    
    if config['Efficiency']:
        df = df.Define('cleanHighPtJet_Eta','cleanJet_Eta[cleanJet_Pt>{}]'.format(JetRecoPtCut))
        df = df.Define('cleanHighPtJet_Phi','cleanJet_Phi[cleanJet_Pt>{}]'.format(JetRecoPtCut))
        df = df.Define('cleanHighPtJet_Eta_PassL1Jet','cleanJet_Eta[cleanJet_L1Pt>={}&&cleanJet_Pt>{}]'.format(L1JetPtCut, JetRecoPtCut))
        df = df.Define('cleanHighPtJet_Phi_PassL1Jet','cleanJet_Phi[cleanJet_L1Pt>={}&&cleanJet_Pt>{}]'.format(L1JetPtCut, JetRecoPtCut))
        
        histos["L1JetvsEtaPhi_Numerator"+suffix] = df.Histo2D(ROOT.RDF.TH2DModel('h_L1Jet{}vsEtaPhi_Numerator'.format(int(L1JetPtCut))+suffix, '', 100,-5,5,100,-3.1416,3.1416), 'cleanHighPtJet_Eta_PassL1Jet','cleanHighPtJet_Phi_PassL1Jet')
        histos["L1JetvsEtaPhi_EtaRestricted"+suffix] = df.Histo2D(ROOT.RDF.TH2DModel('h_L1Jet{}vsEtaPhi_EtaRestricted'.format(int(L1JetPtCut))+suffix, '', 100,-5,5,100,-3.1416,3.1416), 'cleanHighPtJet_Eta','cleanHighPtJet_Phi')
    

    if config['Prefiring']:
        df = df.Define('cleanJet_idxL1EG','FindL1ObjIdx(L1EG_eta, L1EG_phi, cleanJet_Eta, cleanJet_Phi, L1EG_hwIso, -1)')
        df = df.Define('cleanJet_idxL1EG_Bx0','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, cleanJet_Eta, cleanJet_Phi, 0, L1EG_hwIso, -1)')
        df = df.Define('cleanJet_idxL1EG_Bxmin1','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, cleanJet_Eta, cleanJet_Phi, -1, L1EG_hwIso, -1)')
        df = df.Define('cleanJet_idxL1EG_Bxplus1','FindL1ObjIdx_setBx(L1EG_eta, L1EG_phi, L1EG_bx, cleanJet_Eta, cleanJet_Phi, 1, L1EG_hwIso, -1)')
        df = df.Define('cleanJet_L1EG_Pt','GetVal(cleanJet_idxL1EG, L1EG_pt)')
        df = df.Define('cleanJet_L1EG_Bx','GetVal(cleanJet_idxL1EG, L1EG_bx)')

        df = df.Define('cleanJet_idxL1IsoTau','FindL1ObjIdx(L1Tau_eta, L1Tau_phi, cleanJet_Eta, cleanJet_Phi, L1Tau_hwIso, 1)')
        df = df.Define('cleanJet_idxL1IsoTau_Bx0','FindL1ObjIdx_setBx(L1Tau_eta, L1Tau_phi, L1Tau_bx, cleanJet_Eta, cleanJet_Phi, 0, L1Tau_hwIso, 1)')
        df = df.Define('cleanJet_idxL1IsoTau_Bxmin1','FindL1ObjIdx_setBx(L1Tau_eta, L1Tau_phi, L1Tau_bx, cleanJet_Eta, cleanJet_Phi, -1, L1Tau_hwIso, 1)')
        df = df.Define('cleanJet_idxL1IsoTau_Bxplus1','FindL1ObjIdx_setBx(L1Tau_eta, L1Tau_phi, L1Tau_bx, cleanJet_Eta, cleanJet_Phi, 1, L1Tau_hwIso, 1)')
        df = df.Define('cleanJet_L1IsoTau_Pt','GetVal(cleanJet_idxL1IsoTau, L1Tau_pt)')
        df = df.Define('cleanJet_L1IsoTau_Eta','GetVal(cleanJet_idxL1IsoTau, L1Tau_eta)')
        df = df.Define('cleanJet_L1IsoTau_Phi','GetVal(cleanJet_idxL1IsoTau, L1Tau_phi)')
        df = df.Define('cleanJet_L1IsoTau_Bx','GetVal(cleanJet_idxL1IsoTau, L1Tau_bx)')

        df = df.Define('cleanJet_idxL1Jet','FindL1ObjIdx(L1Jet_eta, L1Jet_phi, cleanJet_Eta, cleanJet_Phi)')
        df = df.Define('cleanJet_idxL1Jet_Bx0','FindL1ObjIdx_setBx(L1Jet_eta, L1Jet_phi, L1Jet_bx, cleanJet_Eta, cleanJet_Phi, 0)')
        df = df.Define('cleanJet_idxL1Jet_Bxmin1','FindL1ObjIdx_setBx(L1Jet_eta, L1Jet_phi, L1Jet_bx, cleanJet_Eta, cleanJet_Phi, -1)')
        df = df.Define('cleanJet_idxL1Jet_Bxplus1','FindL1ObjIdx_setBx(L1Jet_eta, L1Jet_phi, L1Jet_bx, cleanJet_Eta, cleanJet_Phi, 1)')
        df = df.Define('cleanJet_L1Jet_Eta','GetVal(cleanJet_idxL1Jet, L1Jet_eta)')
        df = df.Define('cleanJet_L1Jet_Phi','GetVal(cleanJet_idxL1Jet, L1Jet_phi)')

        
        for bx in ['min1', '0', 'plus1'] :
            df = df.Define('cleanJet_L1Jet_Pt_Bx{}'.format(bx), 'GetVal(cleanJet_idxL1Jet_Bx{}, L1Jet_pt)'.format(bx))
            df = df.Define('cleanJet_L1EG_Pt_Bx{}'.format(bx), 'GetVal(cleanJet_idxL1EG_Bx{}, L1EG_pt)'.format(bx))
            df = df.Define('cleanJet_L1IsoTau_Pt_Bx{}'.format(bx), 'GetVal(cleanJet_idxL1IsoTau_Bx{}, L1Tau_pt)'.format(bx))
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1Jet', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=30, probe_str='cleanJet', suffix = suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>500', l1objname='L1Jet', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=30, probe_str='cleanJet', suffix = '_jet500'+suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1EG', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=20, probe_str='cleanJet', suffix = suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>500', l1objname='L1EG', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=20, probe_str='cleanJet', suffix = '_jet500'+suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1IsoTau', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=25, probe_str='cleanJet', suffix = suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1IsoTau', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=5, probe_str='cleanJet', suffix = "_l1isotau5gev"+suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1IsoTau', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=8, probe_str='cleanJet', suffix = "_l1isotau8gev"+suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1IsoTau', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=10, probe_str='cleanJet', suffix = "_l1isotau10gev"+suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>50', l1objname='L1IsoTau', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=15, probe_str='cleanJet', suffix = "_l1isotau15gev"+suffix)
        histos = getprefiringhistos(df, histos, probecondition='cleanJet_Pt>500', l1objname='L1IsoTau', etabinning=[-5., -3., -2.5, -1.3, 0., 1.3, 2.5, 3., 5.], ptbinning=jetmetpt_bins, l1threshold=15, probe_str='cleanJet', suffix = "_l1isotau15gev_jet500"+suffix)

        
    return df, histos


    
def PrefiringVsMjj(df): 
    histos = {}
    histos['mjj'] =  df.Histo1D(ROOT.RDF.TH1DModel('mjj', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj') 

    histos['mjj_unpref_trigrules_barrelbarrel'] =  df.Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_trigrules_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_trigrules_L1FinalORBXmin1_barrelbarrel'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_trigrules_L1FinalORBXmin1_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_trigrules_L1FinalORBXmin2_barrelbarrel'] =  df.Filter('L1_FinalOR_BXmin2').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_trigrules_L1FinalORBXmin2_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_trigrules_endcapendcap'] =  df.Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_trigrules_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_trigrules_L1FinalORBXmin1_endcapendcap'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_trigrules_L1FinalORBXmin1_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_trigrules_L1FinalORBXmin2_endcapendcap'] =  df.Filter('L1_FinalOR_BXmin2').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_trigrules_L1FinalORBXmin2_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')

    #1st bx in trains (can only check BX-1, not BX-2)
    histos['mjj_unpref_1stbx_barrelbarrel'] =  df.Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_1stbx_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_1stbx_L1FinalORBXmin1_barrelbarrel'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_1stbx_L1FinalORBXmin1_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_1stbx_endcapendcap'] =  df.Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_1stbx_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    histos['mjj_unpref_1stbx_L1FinalORBXmin1_endcapendcap'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mjj_unpref_1stbx_L1FinalORBXmin1_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mjj')
    
    return df, histos

def PrefiringVsMll(df): 
    histos = {}
    histos['mll'] =  df.Histo1D(ROOT.RDF.TH1DModel('mll', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll') 
    histos['mll_zoom'] =  df.Histo1D(ROOT.RDF.TH1DModel('mll_zoom', '', 60, 60, 120 ), '_mll') 
    histos['mll_unpref_trigrules_barrelbarrel'] =  df.Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_trigrules_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_trigrules_L1FinalORBXmin1_barrelbarrel'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_trigrules_L1FinalORBXmin1_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_trigrules_L1FinalORBXmin2_barrelbarrel'] =  df.Filter('L1_FinalOR_BXmin2').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_trigrules_L1FinalORBXmin2_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_trigrules_endcapendcap'] =  df.Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_trigrules_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_trigrules_L1FinalORBXmin1_endcapendcap'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_trigrules_L1FinalORBXmin1_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_trigrules_L1FinalORBXmin2_endcapendcap'] =  df.Filter('L1_FinalOR_BXmin2').Filter('(L1_UnprefireableEvent_TriggerRules)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_trigrules_L1FinalORBXmin2_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')

    #1st bx in trains (can only check BX-1, not BX-2)
    histos['mll_unpref_1stbx_barrelbarrel'] =  df.Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_1stbx_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_1stbx_L1FinalORBXmin1_barrelbarrel'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('barrelbarrel').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_1stbx_L1FinalORBXmin1_barrelbarrel', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_1stbx_endcapendcap'] =  df.Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_1stbx_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    histos['mll_unpref_1stbx_L1FinalORBXmin1_endcapendcap'] =  df.Filter('L1_FinalOR_BXmin1').Filter('(L1_UnprefireableEvent_FirstBxInTrain)').Filter('endcapendcap').Histo1D(ROOT.RDF.TH1DModel('mll_unpref_1stbx_L1FinalORBXmin1_endcapendcap', '', len(ht_bins)-1, array('d',ht_bins) ), '_mll')
    

    
    return df, histos

def HFNoiseStudy(df, suffix = ''):
    '''
    Offline study of HF noise.
    '''
    histos={}
    #debugging what happens in the HF 
    dfhfnoise = df.Define('isHFJet','cleanJet_Pt>30&&((cleanJet_Eta>3.0&&cleanJet_Eta<5)||(cleanJet_Eta>-5&&cleanJet_Eta<-3.))' )
    dfhfnoise = dfhfnoise.Define('nHFJets','Sum(isHFJet)')
    dfhfnoise = dfhfnoise.Define('isHFJetPt250','cleanJet_Pt>250&&((cleanJet_Eta>3.0&&cleanJet_Eta<5)||(cleanJet_Eta>-5&&cleanJet_Eta<-3.))' )
    dfhfnoise = dfhfnoise.Filter('Sum(isHFJetPt250)>0')
    dfhfnoise = dfhfnoise.Define('passL1Pt80','cleanJet_L1Pt>80')
    
    dfhfnoise = dfhfnoise.Define('HighPtHFJet_Pt','cleanJet_Pt[isHFJetPt250]')
    dfhfnoise = dfhfnoise.Define('HighPtHFJet_Eta','cleanJet_Eta[isHFJetPt250]')

    dfhfnoise = dfhfnoise.Define('HighPtJet_HFSEtaEta','Jet_hfsigmaEtaEta[Jet_pt>250&&((Jet_eta>3.0&&Jet_eta<5)||(Jet_eta>-5&&Jet_eta<-3.))]')
    dfhfnoise = dfhfnoise.Define('HighPtJet_HFSPhiPhi','Jet_hfsigmaPhiPhi[Jet_pt>250&&((Jet_eta>3.0&&Jet_eta<5)||(Jet_eta>-5&&Jet_eta<-3.))]')
    dfhfnoise = dfhfnoise.Define('HighPtJet_HFCentralEtaStripSize','Jet_hfcentralEtaStripSize[Jet_pt>250&&((Jet_eta>3.0&&Jet_eta<5)||(Jet_eta>-5&&Jet_eta<-3.))]')
    dfhfnoise = dfhfnoise.Define('HighPtJet_HFAdjacentEtaStripSize','Jet_hfadjacentEtaStripsSize[Jet_pt>250&&((Jet_eta>3.0&&Jet_eta<5)||(Jet_eta>-5&&Jet_eta<-3.))]')
    
    
    prefix = ['failL1Jet80', 'passL1Jet80']
    df_passvsfailL1 = [dfhfnoise.Filter('Sum(passL1Pt80&&isHFJetPt250)==0'), dfhfnoise.Filter('Sum(passL1Pt80&&isHFJetPt250)>=1')]
    
    for i, p in enumerate(prefix):
        if i == 0:
            df_passvsfailL1[i] = df_passvsfailL1[i].Filter(stringToPrintHF)
        

        histos[p+'_nhfjets'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_nhfjets'+suffix, '', 100, 0, 100), 'nHFJets')
        histos[p+'_npv'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_npv'+suffix, '', 100, 0, 100), 'PV_npvs')
        histos[p+'_runnb'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_runnb'+suffix, '', len(runnb_bins)-1, runnb_bins), 'run')
        '''
        histos[p+'_photonpt'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_photonpt'+suffix, '', 100, 0, 1000), 'ref_Pt')
        histos[p+'_ptbalance'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_ptbalance'+suffix, '', len(response_bins)-1, response_bins), 'ptbalance')
        histos[p+'_ptbalanceL1'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_ptbalanceL1'+suffix, '', len(response_bins)-1, response_bins), 'ptbalanceL1')
        '''
        histos[p+'_HighPtHFJet_Eta'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_HighPtHFJet_Eta'+suffix, '', 1000, -5, 5), 'HighPtHFJet_Eta')
        histos[p+'_HighPtHFJet_Pt'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'_HighPtHFJet_Pt'+suffix, '', 80, 100, 500), 'HighPtHFJet_Pt')
        histos[p+'_HighPtJet_HFSEtaEtavsPhiPhi'+suffix] = df_passvsfailL1[i].Histo2D(ROOT.RDF.TH2DModel(p+'_HighPtJet_HFSEtaEtavsPhiPhi'+suffix, '', 100, 0, 0.2, 100, 0, 0.2), 'HighPtJet_HFSEtaEta','HighPtJet_HFSPhiPhi')
        histos[p+'_HighPtJet_HFCentralVsAdjacentEtaStripSize'+suffix] = df_passvsfailL1[i].Histo2D(ROOT.RDF.TH2DModel(p+'_HighPtJet_HFCentralVsAdjacentEtaStripSize'+suffix, '', 10, 0, 10, 10, 0, 10), 'HighPtJet_HFCentralEtaStripSize', 'HighPtJet_HFAdjacentEtaStripSize')

        histos[p+'MET_pt'+suffix] = df_passvsfailL1[i].Histo1D(ROOT.RDF.TH1DModel(p+'PuppiMET_pt'+suffix, '', 100,0,500), 'PuppiMET_pt')

    return df, histos
    
def PtBalanceSelection(df):
    '''
    Compute pt balance = pt(jet)/pt(ref)
    ref can be a photon or a Z.
    '''
    
    #Back to back condition
    df = df.Filter('abs(acos(cos(ref_Phi-cleanJet_Phi[0])))>2.9','DeltaPhi(ph,jet)>2.9')

    #Compute Pt balance = pt(jet)/pt(ref) => here ref is a photon
    #Reco first
    df = df.Define('ptbalance','cleanJet_Pt[0]/ref_Pt')
    df = df.Define('ptbalanceL1','L1Jet_pt[cleanJet_idxL1jetbx0[0]]/ref_Pt')
    df = df.Define('probe_Eta','cleanJet_Eta[0]') 
    df = df.Define('probe_Phi','cleanJet_Phi[0]')
    return df

def AnalyzePtBalance(df, suffix = ''):
    histos = {}
    df_JetsBinnedInEta ={}
    histos['L1JetvsEtaPhi'+suffix] = df.Histo3D(ROOT.RDF.TH3DModel('h_L1PtBalanceVsEtaPhi'+suffix, 'ptbalanceL1', 100, -5, 5, 100, -3.1416, 3.1416, 100, 0, 2), 'probe_Eta','probe_Phi','ptbalanceL1')
    for r in config['Regions']:
        region = config['Regions'][r]
        str_bineta = "eta{}to{}".format(region[0], region[1]).replace(".","p")
        df_JetsBinnedInEta[str_bineta] = df.Filter('abs(cleanJet_Eta[0])>={}&&abs(cleanJet_Eta[0])<{}'.format(region[0], region[1]))
        histos['RecoJetvsRunNb'+str_bineta+suffix] = df_JetsBinnedInEta[str_bineta].Histo2D(ROOT.RDF.TH2DModel('h_PtBalanceVsRunNb_{}'.format(str_bineta)+suffix, 'ptbalance', len(runnb_bins)-1, runnb_bins, len(response_bins)-1, response_bins), 'run','ptbalance')
        histos['L1JetvsRunNb'+str_bineta+suffix] = df_JetsBinnedInEta[str_bineta].Histo2D(ROOT.RDF.TH2DModel('h_L1PtBalanceVsRunNb_{}'.format(str_bineta)+suffix, 'ptbalanceL1', len(runnb_bins)-1, runnb_bins, len(response_bins)-1, response_bins), 'run','ptbalanceL1')
        histos['L1JetvsPU'+str_bineta+suffix] = df_JetsBinnedInEta[str_bineta].Histo2D(ROOT.RDF.TH2DModel('h_L1PtBalanceVsPU_{}'.format(str_bineta)+suffix, 'ptbalanceL1', 100, 0, 100, 100, 0, 2), 'PV_npvs','ptbalanceL1')
        # only one jet with pT > 30 GeV
        histos['L1JetvsRunNb_singlejet'+str_bineta+suffix] = df_JetsBinnedInEta[str_bineta].Filter('Sum(isCleanJet)==1','==1 clean jet with p_{T}>30 GeV').Histo2D(ROOT.RDF.TH2DModel('h_L1PtBalanceVsRunNb_singlejet_{}'.format(str_bineta)+suffix, 'ptbalanceL1', len(runnb_bins)-1, runnb_bins, len(response_bins)-1, response_bins), 'run','ptbalanceL1')

    return df, histos


    
def getprefiringhistos(df, histos, probecondition='probe_Pt>20', l1objname='L1Mu/L1EG/L1Jet', etabinning=[], ptbinning=[], l1threshold=22, probe_str='probe', suffix = ''):

    colname = probe_str+'_'+l1objname+'{}'.format(l1threshold)    
        
    df = df.Define(colname+'All_Eta', probe_str+'_Eta['+probecondition+']'.format(l1threshold))
    df = df.Define(colname+'All_Phi', probe_str+'_Phi['+probecondition+']'.format(l1threshold))
    df = df.Define(colname+'All_Pt', probe_str+'_Pt['+probecondition+']'.format(l1threshold))
    df = df.Define(colname+'_runnb', 'return ROOT::VecOps::RVec<int>('+colname+'All_Eta'+'.size(), run);')
    
    for bx in ['min1', '0', 'plus1'] :
        df = df.Define(colname+'Bx{}_Eta'.format(bx), probe_str+'_Eta['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
        df = df.Define(colname+'Bx{}_Phi'.format(bx), probe_str+'_Phi['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
        df = df.Define(colname+'Bx{}_Pt'.format(bx), probe_str+'_Pt['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
        df = df.Define(colname+'Bx{}_runnb'.format(bx), 'return ROOT::VecOps::RVec<int>('+colname+'Bx{}_Eta'.format(bx)+'.size(), run);')


    
    for typeofevents in ['L1_UnprefireableEvent_TriggerRules', 'L1_UnprefireableEvent_FirstBxInTrain' , 'AllEvents'] :
        #        for varstudied in ['eta', 'etaphi', 'etapt'] :
        for bx in ['min1', '0', 'plus1'] :

            cut_typeofevents = typeofevents
            if typeofevents == 'AllEvents':
                cut_typeofevents = 'return true;'
                
            hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_bx'+bx+'_etapt'+suffix            
            histos[hname] = df.Filter(cut_typeofevents).Histo2D(ROOT.RDF.TH2DModel(hname, '', len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d', ptbinning)), colname+'Bx{}_Eta'.format(bx), colname+'Bx{}_Pt'.format(bx))

            hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_bx'+bx+'_etaphi'+suffix
            histos[hname] = df.Filter(cut_typeofevents).Histo2D(ROOT.RDF.TH2DModel(hname, '', 100, -5, 5, 100, -3.1416, 3.1416), colname+'Bx{}_Eta'.format(bx), colname+'Bx{}_Phi'.format(bx))
            hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_bx'+bx+'_eta'+suffix
            histos[hname] = df.Filter(cut_typeofevents).Histo1D(ROOT.RDF.TH1DModel(hname, '', 100, -5, 5), colname+'Bx{}_Eta'.format(bx))
            
            hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_bx'+bx+'_runnb'+suffix
            histos[hname] = df.Filter(cut_typeofevents).Histo1D(ROOT.RDF.TH1DModel(hname, '', len(runnb_bins)-1, runnb_bins), colname+'Bx{}_runnb'.format(bx))
            
            #To be removed
            if typeofevents == 'AllEvents' and suffix.find('_jet500')>=0 and l1objname== 'L1Jet':
                df = df.Define(colname+'Bx{}_L1Jet_Eta'.format(bx), probe_str+'_L1Jet_Eta['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
                df = df.Define(colname+'Bx{}_L1Jet_Phi'.format(bx), probe_str+'_L1Jet_Phi['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
                l1jet_bin = [-5.3, -5.04, -4.8025, -4.627, -4.4505, -4.277, -4.102, -3.926, -3.7515, -3.5765, -3.4015, -3.227, -3.0515, 
                             -2.8945, -2.7,-2.493,-2.329, -2.17725, -2.047, -1.93325, -1.8325] + [ 0.087*i for i in range(-20,21)] + [ 1.8325, 1.93325, 2.047, 2.17725, 2.329, 2.493, 2.7, 2.8945, 3.0515, 3.227,3.4015,3.5765, 3.7515,3.926,4.102,4.277,4.4505,4.627,4.8025,5.04,5.3]
                np_l1jet_bin = np.array(l1jet_bin)
                histos['l1jet30_etavsphi_bx'+bx] = df.Histo2D(ROOT.RDF.TH2DModel('l1jet30_etavsphi_bx'+bx, '', np_l1jet_bin.size-1, np_l1jet_bin, 72, -3.1416, 3.1416), colname+'Bx{}_L1Jet_Eta'.format(bx), colname+'Bx{}_L1Jet_Phi'.format(bx))
            
            if typeofevents == 'AllEvents' and suffix.find('_l1isotau10gev')>=0 and l1objname== 'L1IsoTau':
                df = df.Define(colname+'Bx{}_L1IsoTau_Eta'.format(bx), probe_str+'_L1IsoTau_Eta['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
                df = df.Define(colname+'Bx{}_L1IsoTau_Phi'.format(bx), probe_str+'_L1IsoTau_Phi['+probecondition+'&&'+probe_str+'_'+l1objname+'_Pt_Bx{}>{}]'.format(bx, l1threshold))
                l1jet_bin = [-5.3, -5.04, -4.8025, -4.627, -4.4505, -4.277, -4.102, -3.926, -3.7515, -3.5765, -3.4015, -3.227, -3.0515, 
                             -2.8945, -2.7,-2.493,-2.329, -2.17725, -2.047, -1.93325, -1.8325] + [ 0.087*i for i in range(-20,21)] + [ 1.8325, 1.93325, 2.047, 2.17725, 2.329, 2.493, 2.7, 2.8945, 3.0515, 3.227,3.4015,3.5765, 3.7515,3.926,4.102,4.277,4.4505,4.627,4.8025,5.04,5.3]
                np_l1jet_bin = np.array(l1jet_bin)
                histos['l1isotau10_etavsphi_bx'+bx] = df.Histo2D(ROOT.RDF.TH2DModel('l1isotau10_etavsphi_bx'+bx, '', np_l1jet_bin.size-1, np_l1jet_bin, 72, -3.1416, 3.1416), colname+'Bx{}_L1IsoTau_Eta'.format(bx), colname+'Bx{}_L1IsoTau_Phi'.format(bx))
                
                                            
        #Now denominators
        if typeofevents == 'AllEvents':
                cut_typeofevents = 'return true;'

        hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_Denominator'+'_etapt'+suffix
        histos[hname] = df.Filter(cut_typeofevents).Histo2D(ROOT.RDF.TH2DModel(hname, '', len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d', ptbinning)), colname+'All_Eta',colname+'All_Pt')
        
        hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_Denominator'+'_etaphi'+suffix
        histos[hname] = df.Filter(cut_typeofevents).Histo2D(ROOT.RDF.TH2DModel(hname, '', 100, -5, 5, 100, -3.1416, 3.1416), colname+'All_Eta', colname+'All_Phi')
        
        hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_Denominator'+'_eta'+suffix
        histos[hname] = df.Filter(cut_typeofevents).Histo1D(ROOT.RDF.TH1DModel(hname, '', 100, -5, 5), colname+'All_Eta')

        #Prefiring vs run nb
        hname = l1objname+'{}'.format(l1threshold)+'_'+typeofevents+'_Denominator'+'_runnb'+suffix
        histos[hname] = df.Filter(cut_typeofevents).Histo1D(ROOT.RDF.TH1DModel(hname, '',  len(runnb_bins)-1, runnb_bins), colname+'_runnb')
        

    return histos 
