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
