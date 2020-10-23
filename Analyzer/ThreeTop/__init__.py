
from .ThreeTop_Muon import Muon
from .ThreeTop_Jets import Jet
from .ThreeTop_Electron import Electron
from .ThreeTop_Event import EventWide

from Analyzer import Scheduler, CutApplier
from commons.configs import pre

# Run Specifics
Scheduler.add_step([Muon, Electron])
Scheduler.add_step([Jet])
Scheduler.add_step([EventWide])

channels = ['had', 'one', 'SS', 'OS', 'multi']

# Scale Factors
CutApplier.add_scale_factor("Event_wDecayScale")
# CutApplier.add_scale_factor("Event_pileupScale")
CutApplier.add_scale_factor("Event_genScale")
CutApplier.add_scale_factor("Event_tightLeptonScale")
CutApplier.add_scale_factor("Event_bscale")

# Output variables
CutApplier.add_vars("looseMuon", pre("Muon", ["pt", "eta", "phi", "mass"]), "Muon_fakeMask")
CutApplier.add_vars("tightMuon", pre("Muon", ["pt", "eta", "phi", "mass"]), "Muon_finalMask")
CutApplier.add_vars("looseElectron", pre("Electron", ["pt", "eCorr", "eta", "phi", "mass"]), "Electron_fakeMask")
CutApplier.add_vars("tightElectron", pre("Electron", ["pt", "eCorr", "eta", "phi", "mass"]), "Electron_finalMask")
CutApplier.add_vars("Jets", pre("Jet", ["pt", "eta", "phi", "mass"]), "Jet_jetMask")
CutApplier.add_vars("BJets", pre("Jet", ["pt", "eta", "phi", "mass"]), "Jet_bjetMask")
CutApplier.add_vars("Event_MET", ["MET_pt", "MET_phi"])

CutApplier.add_make_vars("tightLeptons", pre("Lepton", ["pt", "eta", "phi", "id"]), "merge_leptons",
                         (pre("Muon", ["pt", "eta", "phi", "charge"]), "Muon_finalMask"),
                         (pre("Electron", ["pt", "eta", "phi", "charge"]), "Electron_finalMask"))
CutApplier.add_make_vars("looseLeptons", pre("Lepton", ["pt", "eta", "phi", "id"]), "merge_leptons",
                         (pre("Muon", ["pt", "eta", "phi", "charge"]), "Muon_looseMask"),
                         (pre("Electron", ["pt", "eta", "phi", "charge"]), "Electron_looseMask"))

CutApplier.add_vars_derived(
    "Event_variables", pre("Event", ["HT", "channels", "centrality", "sphericity"]))

CutApplier.add_vars_derived(
    "Event_masks", pre("Jet", ["looseBjetMask", "tightBjetMask"]))

# General Cuts
CutApplier.add_cut("Event_MetFilterMask")
CutApplier.add_cut("Event_MET > 25")
#CutApplier.add_cut("Event_trigger2LepHT250Mask")
CutApplier.add_cut("Event_trigger2LepMask")
CutApplier.add_cut("Event_HT > 250")
CutApplier.add_cut("ak.count_nonzero(Jet_jetMask, axis=1) >= 2") # pt > 40
CutApplier.add_cut("ak.count_nonzero(Jet_bjetMask, axis=1) >= 1")

def set_channel(chan):
    if chan == "had":
        CutApplier.add_cut("abs(Event_channels) == 0")
    else:
        CutApplier.add_cut("Muon_ZVeto")
        CutApplier.add_cut("Electron_ZVeto")
        if chan == "one":
            CutApplier.add_cut("abs(Event_channels) == 1")
        if chan == "SS":
            CutApplier.add_cut("Event_channels > 1")
            CutApplier.add_cut("abs(Event_channels) < 30")
        elif chan == "OS":
            CutApplier.add_cut("Event_channels < -1")
            CutApplier.add_cut("abs(Event_channels) < 30")
        else:
            CutApplier.add_cut("abs(Event_channels) >= 30")
