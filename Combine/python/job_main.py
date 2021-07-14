#!/usr/bin/env python3
import logging
from pathlib import Path

from analysis_suite.commons import GroupInfo
from analysis_suite.commons.configs import getGroupDict, get_list_systs

from .card_maker import Card_Maker

import analysis_suite.data.inputs as mva_params

def setup(cli_args):
    group_info = GroupInfo(**vars(cli_args))

    argList = list()
    for year in cli_args.years:
        path = cli_args.workdir / year
        allSysts = get_list_systs(path, cli_args.systs)
        # for syst in allSysts:
        #     argList.append((groupDict, cli_args.workdir, cli_args.train,
        #                         cli_args.apply_model, year, syst))

    return argList

def run(*args):
    pass

def cleanup(cli_args):
    group_info = GroupInfo(mva_params.color_by_group, **vars(cli_args))
    group_list = list(group_info.get_memberMap().keys())
    group_list.remove(cli_args.signal)
    group_list.insert(0, cli_args.signal)

    with Card_Maker(cli_args.workdir, cli_args.years, group_list) as card:
        card.write_systematics(mva_params.systematics)
