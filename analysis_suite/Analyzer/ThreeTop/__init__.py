
from .ThreeTop_Muon import Muon
from .ThreeTop_Jets import Jet
from .ThreeTop_Electron import Electron
from .ThreeTop_Event import EventWide

from analysis_suite.Analyzer.apply_task import ApplyTask
from analysis_suite.commons.configs import pre

channels = ['had', 'one', 'SS', 'OS', 'multi']

# Scale Factors
ApplyTask.add_scale_factor("Event_wDecayScale")
# ApplyTask.add_scale_factor("Event_pileupScale")
ApplyTask.add_scale_factor("Event_genScale")
ApplyTask.add_scale_factor("Event_tightLeptonScale")
ApplyTask.add_scale_factor("Event_bscale")

# Output variables
ApplyTask.add_vars("looseMuon", pre("Muon", ["pt", "eta", "phi", "mass"]), "Muon_fakeMask")
ApplyTask.add_vars("tightMuon", pre("Muon", ["pt", "eta", "phi", "mass"]), "Muon_finalMask")
ApplyTask.add_vars("looseElectron", pre("Electron", ["pt", "eCorr", "eta", "phi", "mass"]), "Electron_fakeMask")
ApplyTask.add_vars("tightElectron", pre("Electron", ["pt", "eCorr", "eta", "phi", "mass"]), "Electron_finalMask")
ApplyTask.add_vars("Jets", pre("Jet", ["pt", "eta", "phi", "mass"]), "Jet_jetMask")
ApplyTask.add_vars("BJets", pre("Jet", ["pt", "eta", "phi", "mass"]), "Jet_bjetMask")
ApplyTask.add_vars("Event_MET", ["MET_pt", "MET_phi"])

ApplyTask.add_make_vars("tightLeptons", pre("Lepton", ["pt", "eta", "phi", "id"]), "merge_leptons",
                         (pre("Muon", ["pt", "eta", "phi", "charge"]), "Muon_finalMask"),
                         (pre("Electron", ["pt", "eta", "phi", "charge"]), "Electron_finalMask"))
ApplyTask.add_make_vars("looseLeptons", pre("Lepton", ["pt", "eta", "phi", "id"]), "merge_leptons",
                         (pre("Muon", ["pt", "eta", "phi", "charge"]), "Muon_looseMask"),
                         (pre("Electron", ["pt", "eta", "phi", "charge"]), "Electron_looseMask"))

ApplyTask.add_derived_vars(
    "Event_variables", pre("Event", ["HT", "channels", "centrality", "sphericity"]))

ApplyTask.add_derived_vars(
    "Event_masks", pre("Jet", ["looseBjetMask", "tightBjetMask"]))

# General Cuts
ApplyTask.add_cut("Event_MetFilterMask")
ApplyTask.add_cut("Event_MET > 25")
#ApplyTask.add_cut("Event_trigger2LepHT250Mask")
# ApplyTask.add_cut("Event_trigger2LepMask")
ApplyTask.add_cut("Event_HT > 250")
ApplyTask.add_cut("ak.count_nonzero(Jet_jetMask, axis=1) >= 2") # pt > 40
ApplyTask.add_cut("ak.count_nonzero(Jet_bjetMask, axis=1) >= 1")

def set_channel(chan):
    pass
#     if chan == "had":
#         ApplyTask.add_cut("abs(Event_channels) == 0")
#     else:
#         ApplyTask.add_cut("Muon_ZVeto")
#         ApplyTask.add_cut("Electron_ZVeto")
#         if chan == "one":
#             ApplyTask.add_cut("abs(Event_channels) == 1")
#         if chan == "SS":
#             ApplyTask.add_cut("Event_channels > 1")
#             ApplyTask.add_cut("abs(Event_channels) < 30")
#         elif chan == "OS":
#             ApplyTask.add_cut("Event_channels < -1")
#             ApplyTask.add_cut("abs(Event_channels) < 30")
#         else:
#             ApplyTask.add_cut("abs(Event_channels) >= 30")
