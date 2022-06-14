#!/usr/bin/env python3
from pathlib import Path
import awkward as ak
import boost_histogram as bh
import gzip
from correctionlib.schemav2 import VERSION, Binning, Category, Correction, CorrectionSet

from analysis_suite.commons import FileInfo, GroupInfo, PlotInfo
from analysis_suite.commons.fake_rate_helper import setup_events, setup_histogram, DataInfo, GraphInfo

def get_pteta(part, flav, wp):
    flav_mask = part.flavor == flav
    wp_mask = part.pass_btag[flav_mask] >= wp

    return ((ak.flatten(part.pt[flav_mask][wp_mask]), abs(ak.flatten(part.eta[flav_mask][wp_mask]))),
            ak.flatten(part.scale(-1)[flav_mask][wp_mask]))

def get_sf(sf, syst):
    val, err = sf.value, sf.variance
    if syst == 'central':
        return val
    else:
        return val + (err if syst=='up' else -err)

def build_pteta(sf, syst):
    npt, neta = sf.axes.size

    pt_content = lambda eta: Binning.parse_obj({
        "nodetype": "binning",
        "input": "pt",
        "edges": sf.axes[0].edges.tolist(),
        "content": [get_sf(sf.hist[pt, eta], syst) for pt in range(npt)],
        "flow": "clamp",
    })
    return Binning.parse_obj({
        "nodetype": "binning",
        "input": "abseta",
        "edges": sf.axes[1].edges.tolist(),
        "content": [pt_content(eta) for eta in range(neta)],
        "flow": "error",
    })

def build_scales(sf):
    build_flavor = lambda subsf, syst : Category.parse_obj({
        "nodetype": "category",
        "input": "flavor",
        "content": [ {"key": key, "value": build_pteta(value, syst) } for key, value in subsf.items() ],
    })
    build_wp = lambda subsf, syst : Category.parse_obj({
        "nodetype": "category",
        "input": "working_point",
        "content": [ {"key": key, "value": build_flavor(value, syst) } for key, value in sf.items() ],
    })
    return Category.parse_obj({
        "nodetype": "category",
        "input": "systematic",
        "content": [{"key": syst, "value": build_wp(sf, syst) } for syst in systs],
    })


year="2016"
jet_flavs = [0, 4, 5]
wps = {"L": 1, "M": 2, "T": 3}
systs = ['central', 'down', 'up']
weights = {wp: dict() for wp in wps.keys()}

finfo = FileInfo()
color_by_group = {
    "data": "black",
    "DY_ht": "goldenrod",
    "DY": "goldenrod",
    "ttbar_lep": 'royalblue',
    "VV": 'mediumorchid',
    'other': 'seagreen',
}
ginfo = GroupInfo(color_by_group)
lumi = PlotInfo.lumi[year]
GraphInfo.lumi = lumi

mc_info = DataInfo(Path("beff.root"), year)
mc_info.setup_member(ginfo, finfo, "other")


ptbins = bh.axis.Variable([20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120, 150, 200, 300, 400, 600,])
etabins = bh.axis.Regular(7, 0, 2.8)
pteta = GraphInfo("", "", (ptbins, etabins), lambda vg, chan: get_pteta(vg.BJets, *chan))

output = setup_events(mc_info, "Signal")
for flav in jet_flavs:
    all_hist = setup_histogram("", output["other"], (flav, 0), pteta)
    wp_dict = {wp_name: setup_histogram("", output["other"], (flav, wp_id), pteta) for wp_name, wp_id in wps.items()}

    for wp_name, wp_id in wps.items():
        wp_hist = setup_histogram("", output["other"], (flav, wp_id), pteta)
        weights[wp_name][flav] = wp_hist/all_hist

cset = CorrectionSet.parse_obj({
    "schema_version": VERSION,
    "corrections": [
        Correction.parse_obj({
            "version": 1,
            "name": "SS",
            "description": "BTagging efficiencies for different flavor jets in 3Top-2lepton-SS signal region",
            "inputs": [
                {"name": "systematic", "type": "string",
                 "description": "Central value and shifts (statistical only) in efficiency"},
                {"name": "working_point", "type": "string",
                 "description": "Working point to get efficiency"},
                {"name": "flavor", "type": "int",
                 "description": "hadron flavor definition: 5=b, 4=c, 0=udsg"},
                {"name": "abseta", "type": "real", "description": "Jet abseta"},
                {"name": "pt", "type": "real", "description": "Jet pt"},
            ],
            "output": {"name": "weight", "type": "real", "description": "Efficiency of passing Btag cut"},
            "data": build_scales(weights),
        })
    ],
})

with gzip.open("examples.json.gz", "wt") as fout:
    fout.write(cset.json(exclude_unset=True, indent=4))
