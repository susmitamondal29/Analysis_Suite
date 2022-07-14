#!/usr/bin/env python3
from pathlib import Path
import gzip
import argparse
import numpy as np
from correctionlib.schemav2 import VERSION, Binning, Category, Correction, CorrectionSet, Formula, FormulaRef

xcorr = {
    "2016pre" : {
        "type1" : {
            "mc": [0.188743, -0.136539],
            "runB": [0.0214894 , 0.188255],
            "runC": [0.032209 , -0.067288],
            "runD": [0.0293663 , -0.21106],
            "runE": [0.0132046 , -0.20073],
            "runF": [0.0543566 , -0.816597],
        },
        "puppi" : {
            "mc": [0.0060447, 0.4183],
            "runB": [0.00109025, 0.338093],
            "runC": [0.00271913, 0.342268],
            "runD": [0.00254194, 0.305264],
            "runE": [0.00358835, 0.225435],
            "runF": [-0.0056759, 0.454101],
        },
    },
    "2016post" : {
        "type1" : {
            "mc": [0.153497, 0.231751],
            "runF": [-0.134616 , 0.89965],
            "runG": [-0.121809 , 0.584893],
            "runH": [-0.0868828 , 0.703489],
        },
        "puppi" : {
            "mc": [0.0058341, 0.395049],
            "runF": [-0.0234421, 0.371298],
            "runG": [-0.0182134, 0.335786],
            "runH": [-0.015702, 0.340832],
        },
    },
    "2017" : {
        "type1" : {
            "mc": [0.300155, -1.90608],
            "runB": [0.211161 , -0.419333],
            "runC": [0.185184 , 0.164009],
            "runD": [0.201606 , -0.426502],
            "runE": [0.162472 , -0.176329],
            "runF": [0.210639 , -0.72934],
        },
        "puppi" : {
            "mc": [0.0102265, 0.446416],
            "runB": [0.00382117, 0.666228],
            "runC": [0.00110699, 0.747643],
            "runD": [0.00141442, 0.721382],
            "runE": [-0.00593859, 0.851999],
            "runF": [-0.00765682, 0.945001],
        },
    },
    "2018" : {
        "type1" : {
            "mc": [-0.183518, -0.546754],
            "runA": [-0.263733 , 1.91115],
            "runB": [-0.400466 , 3.05914],
            "runC": [-0.430911 , 1.42865],
            "runD": [-0.457327 , 1.56856],
        },
        "puppi" : {
            "mc": [0.0214557, -0.969428],
            "runA": [0.0073377, -0.0250294],
            "runB": [-0.00434261, -0.00892927],
            "runC": [-0.00198311, -0.37026],
            "runD": [-0.00220647, -0.378141],
        },
    },
}

ycorr = {
    "2016pre" : {
        "type1": {
            "mc": [-0.0127927, -0.117747],
            "runB": [-0.0876624 , -0.812885],
            "runC": [-0.113917 , -0.743906],
            "runD": [-0.11331 , -0.815787],
            "runE": [-0.134809 , -0.679068],
            "runF": [-0.114225 , -1.17266],
        },
        "puppi" : {
            "mc": [-0.008331, 0.0990046],
            "runB": [0.00356058, -0.128407],
            "runC": [-0.00187386, -0.104],
            "runD": [0.00177408, -0.164639],
            "runE": [0.000444268, -0.180479],
            "runF": [0.00962707, -0.35731],
        },
    },
    "2016post": {
        "type1" : {
            "mc": [-0.00731978, -0.243323],
            "runF": [-0.0397736 , -1.0385],
            "runG": [-0.0558974 , -0.891234],
            "runH": [-0.0888774 , -0.902632],
        },
        "puppi" : {
            "mc": [-0.00971595, 0.101288],
            "runF": [0.00997438, -0.0809178],
            "runG": [0.0063338, -0.093349],
            "runH": [0.00544957, -0.199093],
        },
    },
    "2017": {
        "type1" : {
            "mc": [-0.300213, 2.02232],
            "runB": [-0.251789 , 1.28089],
            "runC": [-0.200941 , 0.56853],
            "runD": [-0.188208 , 0.58313],
            "runE": [-0.138076 , 0.250239],
            "runF": [-0.198626 , -1.028],
        },
        "puppi" : {
            "mc": [-0.0198663, -0.243182],
            "runB": [-0.0109034, -0.172188],
            "runC": [0.0012184, -0.303817],
            "runD": [0.0011873, -0.21646],
            "runE": [0.0075425, -0.245956],
            "runF": [0.0154974, -0.804176],
        },
    },
    "2018" : {
        "type1" : {
            "mc": [-0.192263, 0.42121],
            "runA": [-0.0431304 , 0.112043],
            "runB": [-0.146125 , 0.533233],
            "runC": [-0.0620083 , 1.46021],
            "runD": [-0.0684071 , 0.928372],
        },
        "puppi" : {
            "mc": [-0.0167134, -0.199296],
            "runA": [0.000406059, -0.0417346],
            "runB": [-0.00234695, -0.20381],
            "runC": [0.016127, -0.402029],
            "runD": [0.0160244, -0.471053],
        },
    },
}

runs = {
    "2016pre":     [0, 272007, 275657, 276315, 276831, 277772, np.inf],
    "2016post": [0, 278801, 278820, 280919, np.inf],
    "2017":   [0, 297020, 299337, 302030, 303435, 304911, np.inf],
    "2018": [0, 315252, 316998, 319313, 320394, np.inf],
}


def build_scales(data, year_run):
    build_funcs = lambda c1, c2 : Binning.parse_obj({
        "nodetype": "binning",
        "input": "npv",
        "edges": [0, 100],
        "flow": "clamp",
        "content": [
            FormulaRef.parse_obj({
                "nodetype": "formularef",
                "index": 0,
                "parameters": [c1, c2],
            })
        ],
    })

    build_runs = lambda d: Binning.parse_obj({
        "nodetype": "binning",
        "input": "run",
        "edges": year_run,
        "content": [build_funcs(eqn_vals[0], eqn_vals[1]) for eqn_vals in d.values()],
        "flow": "clamp",
    })

    return Category.parse_obj({
        "nodetype": "category",
        "input": "type",
        "content": [
            {"key": "MET", "value": build_runs(data["type1"])},
            {"key": "PuppiMET", "value": build_runs(data['puppi'])}
        ],
    })


def create_corr(name, desc, data, year_run):
    return Correction.parse_obj({
        "version": 1,
        "name": name,
        "description": desc,
        "inputs": [
            {"name": "type", "type": "string", "description": "PF MET vs PUPPI MET"},
            {"name": "run", "type": "real", "description": "Run Number"},
            {"name": "npv", "type": "real", "description": "Number of primary vertices"},
        ],
        "output": {"name": "weight", "type": "real", "description": "Value to correct the MET"},
        "generic_formulas": [
            Formula.parse_obj({
                "nodetype": "formula",
                "expression": "[0]*x + [1]",
                "parser": "TFormula",
                "variables": ["npv"],
            })
        ],
        "data": build_scales(data, year_run),
    })

years = ["2016pre", '2016post', '2017', '2018']

for year in years:
    cset = CorrectionSet.parse_obj({
        "schema_version": VERSION,
        "corrections": [
            create_corr("x_correction", "MET corrections for x coordinate", xcorr[year], runs[year]),
            create_corr("y_correction", "MET corrections for x coordinate", ycorr[year], runs[year]),
        ],
    })
    basePath = Path(f'{__file__}').parents[1]
    basePath /= 'data/POG/USER/'+year+("VFP" if "2016" in year else "")+"_UL"
    with gzip.open(basePath / "met_xy.json.gz", "wt") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
