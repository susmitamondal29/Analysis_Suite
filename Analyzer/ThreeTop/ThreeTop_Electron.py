#!/usr/bin/env python3

import uproot4 as uproot
import awkward1 as ak
import numpy as np
import numba
import math

from Analyzer import AnalyzeTask
from Analyzer.Common import deltaR, jetRel, in_zmass, cartes
from commons.configs import pre

class Electron(AnalyzeTask):
    def __init__(self, task):
        super().__init__(task)

        pteta = pre("Electron", ["pt", "eCorr", "eta"])
        mva_vars = pteta + Electron.mva_vars

        self.add_job("loose_mask", outmask = "Electron_basicLooseMask",
                     invars = Electron.loose)
        self.add_job("trigger_emu", outmask = "Electron_triggerEmuMask",
                     inmask = "Electron_basicLooseMask", invars = Electron.emu)
        self.add_job("mva_loose", outmask = "Electron_looseMask",
                     inmask = "Electron_triggerEmuMask", invars = mva_vars)

        self.add_job("looseIdx", outmask = "Electron_looseIndex",
                     inmask = "Electron_looseMask",
                     invars = ["Electron_pt"])

        self.add_job("fake_mask", outmask = "Electron_basicFakeMask",
                     inmask = "Electron_looseMask", invars = Electron.fake)
        self.add_job("closeJet", outmask = ["Electron_closeJetIndex", "Electron_closeJetDR"],
                     inmask = "Electron_basicFakeMask", invars = Electron.close_jet)
        self.add_job("fullIso", outmask = "Electron_fakeMask",
                     inmask = "Electron_basicFakeMask", invars = Electron.v_fullIso,
                     addvals = [(None, "Electron_closeJetIndex")])

        self.add_job("tight_mask", outmask = "Electron_basicTightMask",
                     inmask = "Electron_fakeMask", invars = Electron.tight)
        self.add_job("mva_tight", outmask = "Electron_finalMask",
                     inmask = "Electron_basicTightMask", invars = mva_vars)

        self.add_job("pass_zveto", outmask = "Electron_ZVeto",
                     inmask = "Electron_looseMask", invars = Electron.elec_part,
                     addvals = [("Electron_finalMask", "Electron_looseIndex")])

        self.add_job("lep_lowHT_sf", outmask = "Electron_lowHTScale",
                     inmask = "Electron_looseMask", invars = pteta)
        self.add_job("lep_highHT_sf", outmask = "Electron_highHTScale",
                     inmask = "Electron_looseMask", invars = pteta)
        self.add_job("lep_GSF_sf", outmask = "Electron_GSFScale",
                     inmask = "Electron_looseMask", invars = ["Electron_eta"])
        

    # Numba methods
    loose = pre("Electron", ["pt", "eCorr", "eta", "convVeto", "lostHits",
                             "miniPFRelIso_all", "dz", "dxy"])
    @staticmethod
    @numba.vectorize('b1(f4,f4,f4,b1,u1,f4,f4,f4)')
    def loose_mask(pt, eCorr, eta, convVeto, lostHits, iso, dz, dxy):
        return (
            pt/eCorr > 7 and
            abs(eta) < 2.5 and
            convVeto  and
            lostHits <= 1 and
            iso < 0.4 and
            abs(dz) < 0.1 and
            abs(dxy) < 0.05
           )

    emu = pre("Electron", ["eta", "sieie", "hoe", "eInvMinusPInv"])
    @staticmethod
    @numba.vectorize('b1(f4,f4,f4,f4)')
    def trigger_emu(eta, sieie, hoe, eInvMinusPInv):
        passed = (abs(eInvMinusPInv) < 0.01 and hoe < 0.08)
        if passed:
            return ((abs(eta) < 1.479 and sieie < 0.011) or
               (abs(eta) >= 1.479 and sieie < 0.031))
        else:
            return False

    fake = pre("Electron", ["pt", "eCorr", "sip3d", "tightCharge", "lostHits"])
    @staticmethod
    @numba.vectorize('b1(f4,f4,f4,i4,u1)')
    def fake_mask(pt, eCorr, sip3d, tightCharge, lostHits):
        return (
            pt/eCorr >= 10 and
            sip3d < 4 and
            lostHits == 0 and
            tightCharge == 2
        )


    tight = pre("Electron", ["pt", "eCorr", "miniPFRelIso_all",
                             "dr03EcalRecHitSumEt", "dr03HcalDepth1TowerSumEt",
                             "dr03TkSumPt"])
    @staticmethod
    @numba.vectorize('b1(f4,f4,f4,f4,f4,f4)')
    def tight_mask(pt, eCorr, iso, EcalSumEt, HcalSumEt, TkSumPt):
        pt_cor = pt/eCorr
        return (
            # pt/eCorr > 20 and
            pt_cor > 15 and
            iso < 0.12 and
            EcalSumEt / pt_cor < 0.45 and
            HcalSumEt / pt_cor < 0.25 and
            TkSumPt / pt_cor < 0.2
        )

    @staticmethod
    @numba.jit(nopython=True)
    def looseIdx(events, builder):
        for event in events:
            builder.begin_list()
            for eidx in range(len(event.Electron_pt)):
                builder.integer(eidx)
            builder.end_list()

    close_jet = ["Electron_eta", "Electron_phi", "Jet_eta", "Jet_phi"]
    @staticmethod
    def closeJet(events):
        leta, jeta = cartes(events.Electron_eta, events.Jet_eta)
        lphi, jphi = cartes(events.Electron_phi, events.Jet_phi)
        dr = (jeta-leta)**2 + (jphi-lphi)**2
        dr_idx = ak.argmin(dr, axis=-1) % ak.count(events.Jet_eta, axis=-1)
        dr_min = ak.min(dr, axis=-1)
        return ak.zip((dr_idx, dr_min))

    v_fullIso = pre("Electron", ["pt", "eta", "phi"]) + pre("Jet", ["pt", "eta", "phi"])
    @staticmethod
    def fullIso(events):
        I2 = 0.8
        I3_pow2 = 7.2**2

        closeJet_pt = events.Jet_pt[events.Electron_closeJetIndex]
        closeJet_eta = events.Jet_eta[events.Electron_closeJetIndex]
        closeJet_phi = events.Jet_phi[events.Electron_closeJetIndex]
        jetrel = jetRel(events.Electron_pt, events.Electron_eta,
                        events.Electron_phi, closeJet_pt,
                        closeJet_eta, closeJet_phi)
        pass_I2 = (events.Electron_pt/closeJet_pt) > I2
        pass_I3 = jetrel > I3_pow2
        return pass_I2 or pass_I3

    elec_part = pre("Electron", ["pt", "eta", "phi", "charge"])
    @staticmethod
    def pass_zveto(events):
        tpt, lpt = cartes(events.Electron_pt[events.Electron_looseIndex], events.Electron_pt)
        teta, leta = cartes(events.Electron_eta[events.Electron_looseIndex], events.Electron_eta)
        tphi, lphi = cartes(events.Electron_phi[events.Electron_looseIndex], events.Electron_phi)
        tq, lq = cartes(events.Electron_charge[events.Electron_looseIndex], events.Electron_charge)

        isOS = lq*tq < 0
        zmass = in_zmass(tpt[isOS], teta[isOS], tphi[isOS],
                         lpt[isOS], leta[isOS], lphi[isOS])
        return ak.sum(zmass, axis=-1) != 0


    @staticmethod
    @numba.vectorize('f4(f4,f4,f4)')
    def lep_lowHT_sf(pt, eCorr, eta):
        pt_cor = pt/eCorr
        sf = np.array([[0.9149, 0.9768, 1.0781, 0.9169, 1.1100],
                       [0.9170, 0.9497, 0.9687, 0.9356, 0.9894 ],
                       [0.9208, 0.9483, 0.9923, 0.9438, 0.9781],
                       [0.9202, 0.9514, 0.9827, 0.9480, 0.9627],
                       [0.9207, 0.9481, 0.9848, 0.9480, 0.9477],
                       [0.9472, 0.9333, 0.9934, 0.9383, 0.9597]])
        pt_edges = np.array([20, 30, 40, 50, 100, 14000])
        eta_edges = np.array([0.8, 1.442, 1.566, 2., 2.5])
        return sf[np.argmax(pt_cor <= pt_edges), np.argmax(abs(eta) <= eta_edges)]
    
    @staticmethod
    @numba.vectorize('f4(f4,f4,f4)')
    def lep_highHT_sf(pt, eCorr, eta):
        pt_cor = pt/eCorr
        sf = np.array([[0.9158, 0.9820, 1.0756, 0.9203, 1.1124],
                       [0.9177, 0.9499, 0.9710, 0.9370, 0.9904],
                       [0.9210, 0.9472, 0.9927, 0.9443, 0.9785],
                       [0.9213, 0.9515, 0.9830, 0.9480, 0.9628],
                       [0.9212, 0.9483, 0.9845, 0.9480, 0.9483],
                       [0.9469, 0.9429, 0.9932, 0.9455, 0.9592]])
        pt_edges = np.array([20, 30, 40, 50, 100, 14000])
        eta_edges = np.array([0.8, 1.442, 1.566, 2., 2.5])
        return sf[np.argmax(pt_cor <= pt_edges), np.argmax(abs(eta) <= eta_edges)]

    @staticmethod
    @numba.vectorize('f4(f4)')
    def lep_GSF_sf(eta):
        sf = np.array([1.1703, 1.0085, 1.0105, 1.0052, 0.9979, 0.9917, 0.9865,
                       0.9616, 0.9867, 0.9775, 0.9694, 0.9664, 0.9633, 0.9600,
                       0.9662, 0.9796, 0.9766, 0.9807, 0.9867, 0.9867, 0.9707,
                       0.9897, 0.9959, 0.9897, 0.9949, 0.9928, 0.9666, 0.8840])
        eta_edges = np.array([-2.4, -2.3, -2.2, -2.0, -1.8, -1.63, -1.566,
                              -1.444, -1.2, -1.0, -0.6, -0.4, -0.2, 0.0, 0.2,
                              0.4, 0.6, 1.0, 1.2, 1.444, 1.566, 1.63, 1.8, 2.0,
                              2.2, 2.3, 2.4, 2.5])
        return sf[np.argmax(eta <= eta_edges)]
