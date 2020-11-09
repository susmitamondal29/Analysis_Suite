#!/usr/bin/env python3
import numba
import math
import numpy as np
import awkward1 as ak

@numba.jit(nopython=True)
def deltaR(lphi, leta, jphi, jeta):
    dphi = abs(lphi - jphi)
    if (dphi > math.pi):
        dphi = 2*math.pi - dphi
    return (leta - jeta)**2 + dphi**2

@numba.vectorize('f4(f4,f4,f4,f4,f4,f4)')
def jetRel(lpt, leta, lphi, jpt, jeta, jphi):
    p_jet = jpt*math.cosh(jeta)
    p_lep = lpt*math.cosh(leta)
    p_dot = jpt*lpt*(math.cosh(jeta - leta) - math.cos(jphi - lphi))
    return (p_dot*(2*p_jet*p_lep - p_dot)) / ((p_jet - p_lep)**2 + 2*p_dot)

@numba.vectorize('f4(f4,f4,f4,f4,f4,f4)')
def in_zmass(lpt, leta, lphi, Lpt, Leta, Lphi):
    delta = 15
    zMass = 91.188
    up = zMass + delta
    down = zMass - delta
    mass = math.sqrt(2*lpt*Lpt*(math.cosh(leta-Leta) - math.cos(lphi-Lphi)))
    return mass < 12 or (mass > down and mass < up)

def cartes(arr1, arr2):
    return ak.unzip(ak.cartesian([arr1, arr2], nested=True))

@numba.jit(nopython=True)
def merge_leptons(events, builder):
    for event in events:
        builder.begin_list()
        midx, eidx = 0, 0
        for _ in range(len(event.Muon_pt) +len(event.Electron_pt)):
            builder.begin_tuple(4)
            if (midx != len(event.Muon_pt) and
                (eidx == len(event.Electron_pt) or
                 event.Muon_pt[midx] > event.Electron_pt[eidx])):
                builder.index(0).real(event.Muon_pt[midx])
                builder.index(1).real(event.Muon_eta[midx])
                builder.index(2).real(event.Muon_phi[midx])
                builder.index(3).integer(event.Muon_charge[midx]*13)
                midx += 1
            else:
                builder.index(0).real(event.Electron_pt[eidx])
                builder.index(1).real(event.Electron_eta[eidx])
                builder.index(2).real(event.Electron_phi[eidx])
                builder.index(3).integer(event.Electron_charge[eidx]*11)
                eidx += 1
            builder.end_tuple()
        builder.end_list()


@numba.jit(nopython=True)
def true_in_list(idx_list, shape, builder, useFalse=False):
    for evt in range(len(shape)):
        builder.begin_list()
        for idx in range(shape[evt]):
            idx_in_list = useFalse
            for sub_idx in range(len(idx_list[evt])):
                if idx == idx_list[evt][sub_idx]:
                    idx_in_list = not useFalse
            builder.boolean(idx_in_list)
        builder.end_list()
