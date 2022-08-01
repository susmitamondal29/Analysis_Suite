#!/usr/bin/env python3
import uproot

from .card_maker import Card_Maker

from analysis_suite.commons import GroupInfo, PlotInfo
from analysis_suite.commons.configs import get_list_systs, checkOrCreateDir
from analysis_suite.Plotting.plotter import Plotter
import analysis_suite.data.inputs as inputs
from analysis_suite.data.plotInfo.plotInfo import combine

def setup(cli_args):
    group_info = GroupInfo(inputs.color_by_group, **vars(cli_args))
    allSysts = get_list_systs(cli_args.workdir, cli_args.tool)

    workdir = cli_args.workdir / "combine"
    checkOrCreateDir(workdir)

    ginfo = GroupInfo(inputs.color_by_group)
    groups = ginfo.setup_groups()

    argList = list()
    for cr, graph in combine.items():
        region, graph = graph
        for year in cli_args.years:
            inpath = cli_args.workdir/year
            outfile = workdir / f'{graph.name}_{year}_{cr}.root'
            argList.append((inpath, outfile, graph, region, groups, year, allSysts))

    return argList


def run(inpath, outfile, graph, region, groups, year, systs):
    print(outfile)
    with uproot.recreate(outfile) as f:
        for syst in systs:
            plotter = Plotter(inpath/f'test_{syst}_{region}.root', groups)
            plotter.fill_hists(graph)
            syst = syst.replace("_up", "Up").replace("_down", "Down")
            if syst == "Nominal":
                f[f"data_obs_{syst}"] = plotter.get_sum(groups.keys(), graph).hist
            for group, hist in plotter.get_hists(graph.name).items():
                f[f"{group}_{syst}"] = hist.hist


def cleanup(cli_args):
    workdir = cli_args.workdir / "combine"
    ginfo = GroupInfo(inputs.color_by_group)
    groups = ginfo.setup_groups()

    for cr, graph in combine.items():
        for year in cli_args.years:
            with Card_Maker(workdir, year, cr, list(groups.keys()), graph[1].name) as card:
                card.write_systematics(inputs.systematics)
