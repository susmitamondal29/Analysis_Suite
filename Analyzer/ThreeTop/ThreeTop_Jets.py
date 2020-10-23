#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba

from Analyzer.Process import Process
from commons.configs import pre

class Jet(Process):
    def __init__(self, process):
        super().__init__(process)

        self.add_job("closeJet", outmask="Jet_rmCloseJet", vals = Jet.close_jet,
                     addvals = [("Electron_fakeMask","Electron_closeJetIndex"),
                                ("Muon_fakeMask", "Muon_closeJetIndex")])
        self.add_job("loose_jet_mask", outmask = "Jet_looseJetMask",
                     inmask="Jet_rmCloseJet", vals = Jet.jet)
        self.add_job("jet_mask", outmask = "Jet_jetMask",
                     inmask="Jet_looseJetMask", vals = ["Jet_pt"])
        self.add_job("loose_bjet_mask", outmask = "Jet_looseBjetMask",
                     inmask="Jet_looseJetMask", vals = Jet.btag)
        self.add_job("bjet_mask", outmask = "Jet_bjetMask",
                     inmask="Jet_looseJetMask", vals = Jet.btag)
        self.add_job("tight_bjet_mask", outmask = "Jet_tightBjetMask",
                     inmask="Jet_looseJetMask", vals = Jet.btag)
        self.add_job("get_bscale", outmask = "Event_bscale",
                     inmask = "Jet_looseJetMask", vals = Jet.bscale,
                     addvals = [(None, ["Jet_jetMask", "Jet_bjetMask"])])

    # Numba methods
    close_jet = ["Muon_eta", "Muon_phi", "Jet_eta", "Jet_phi",
                 "Electron_eta", "Electron_phi"]
    @staticmethod
    @numba.jit(nopython=True)
    def closeJet(events, builder):
        j = 0
        for event in events:
            builder.begin_list()
            close_jet = []
            for i in range(len(event.Electron_closeJetIndex)):
                if event.Electron_closeJetIndex[i][1] < 0.16:
                    close_jet.append(int(event.Electron_closeJetIndex[i][0]))
            for i in range(len(event.Muon_closeJetIndex)):
                if event.Muon_closeJetIndex[i][1] < 0.16:
                    close_jet.append(int(event.Muon_closeJetIndex[i][0]))
            for jidx in range(len(event.Jet_eta)):
                isClose = jidx in close_jet
                builder.boolean(not isClose)
            builder.end_list()
            j+=1


    jet = pre("Jet", ["pt", "eta", "jetId"])
    @staticmethod
    @numba.vectorize('b1(f4,f4,i4)')
    def loose_jet_mask(pt, eta, jetId):
        jetId_key = 0b11
        return (
            pt > 25 and
            abs(eta) < 2.4 and
            (jetId & jetId_key) != 0
        )

    
    @staticmethod
    @numba.vectorize('b1(f4)')
    def jet_mask(pt):
        return (pt > 40)


    @staticmethod
    def eval_sf(x, flav):
        if abs(flav) == 5:  # PID_BJET = 5
            return eval(Jet.b_form[1])
        elif abs(flav) == 4:  # PID_CJET = 4
            return eval(Jet.c_form[1])
        else:
            return eval(Jet.udsg_form[1])


    bscale = pre("Jet", ["pt", "eta", "hadronFlavour"])
    def get_bscale(self, events):
        jet_notb = events.Jet_jetMask and (events.Jet_bjetMask == False)

        sf = Jet.get_sf(events.Jet_pt, events.Jet_hadronFlavour)
        eff = Jet.get_eff(events.Jet_pt[jet_notb], events.Jet_eta[jet_notb],
                          events.Jet_hadronFlavour[jet_notb])

        tagged_b = ak.prod(sf[events.Jet_bjetMask], axis=-1)
        untagged_b = ak.prod((1-sf[jet_notb]*eff)/(1-eff), axis=-1)
        return tagged_b*untagged_b
