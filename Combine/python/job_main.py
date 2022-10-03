#!/usr/bin/env python3
import uproot

from .card_maker import Card_Maker

from analysis_suite.commons.info import GroupInfo
from analysis_suite.commons.configs import get_list_systs, get_inputs
from analysis_suite.plotting.plotter import Plotter
from analysis_suite.data.plotInfo.plotInfo import combine

def setup(cli_args):
    color_by_group = get_inputs(cli_args.workdir).color_by_group
    group_info = GroupInfo(color_by_group, **vars(cli_args))
    allSysts = get_list_systs(cli_args.workdir, cli_args.tool, cli_args.systs)
    workdir = cli_args.workdir / "combine"
    workdir.mkdir(exist_ok=True)

    ginfo = GroupInfo(color_by_group)
    groups = ginfo.setup_groups()

    argList = list()
    for cr, graph in combine.items():
        region, graph = graph
        for year in cli_args.years:
            inpath = cli_args.workdir/year
            argList.append((inpath, cli_args.workdir, graph, region, groups, year, allSysts))
    return argList


def run(inpath, workdir, graph, region, groups, year, systs):
    outfile = workdir / f'{graph.name}_{year}_{region}.root'
    signalName = 'ttt'
    ginfo = GroupInfo(get_inputs(workdir).color_by_group)

    with uproot.recreate(outfile) as f:
        for syst in systs:
            if syst != "Nominal":
                continue
            plotter = Plotter(inpath/f'test_{syst}_{region}.root', groups)
            plotter.fill_hists(graph, ginfo)
            syst = syst.replace("_up", "Up").replace("_down", "Down")
            if syst == "Nominal":
                f[f"data_obs"] = plotter.get_sum(groups.keys(), graph).hist
            for group, hist in plotter.get_hists(graph.name).items():
                if not hist: continue
                if syst == "Nominal":
                    f[group] = hist.hist
                else:
                    f[f'{syst}/{group}'] = hist.hist


def cleanup(cli_args):
    workdir = cli_args.workdir / "combine"
    inputs = get_inputs(cli_args.workdir)
    ginfo = GroupInfo(inputs.color_by_group)
    groups = order_list(ginfo.setup_groups(), cli_args.signal)
    allSysts = get_list_systs(cli_args.workdir, cli_args.tool, cli_args.systs)
    syst_objs = list()

    for syst in inputs.systematics:
        if f'{syst.name}_up' in allSysts and f'{syst.name}_down' in allSysts:
            syst_objs.append(syst)
        if syst.syst_type == "lnN":
            syst_objs.append(syst)

    for cr, graph in combine.items():
        for year in cli_args.years:
            with Card_Maker(workdir, year, cr, groups, graph[1].name) as card:
                card.write_systematics(syst_objs)
                card.add_rateParam('ttz')

def order_list(groups, sig):
    glist = list(groups.keys())
    if glist[0] != sig:
        idx = glist.index(sig)
        glist[0], glist[idx] = glist[idx], glist[0]
    return glist
