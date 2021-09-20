#!/usr/bin/env python3
import subprocess
import argparse
from pathlib import Path
import sys
import numpy as np
from analysis_suite.commons.plot_utils import plot
import uproot4 as uproot

def runCombine(command, output=True):
    helper = Path("./scripts/helper_functions.sh")
    with subprocess.Popen([ f"{helper.resolve()} run_combine {command}"], shell=True,
                          cwd=runCombine.work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            if output:
                print(line.decode('utf8'), end="")
    if output:
        print("\n")

def get_cli():
    parser = argparse.ArgumentParser(prog="main", description="")
    parser.add_argument("type", type=str, choices=["impact", "sig", "hybrid", "sig_scan",
                                                   "fit", "asymtotic", "help"])
    parser.add_argument("-d", "--workdir", required=True, type=lambda x : Path(x)/"combine",
                        help="Working Directory")
    parser.add_argument("-f", "--fit_var", required=True,
                        help="Variable used for fitting")
    if len(sys.argv) == 1:
        parser.parse_args()
    blind_text = "--run blind" if sys.argv[1] == "asymtotic" else "-t -1"
    parser.add_argument("--blind", default="", action="store_const", const=blind_text)
    parser.add_argument("-r", default=1)

    return parser.parse_args()

def need_redo_t2w(workdir, cardName):
    txt_card = workdir / cardName.replace("root", "txt")
    root_card = workdir / cardName
    return not root_card.exists() or txt_card.stat().st_mtime > root_card.stat().st_mtime


if __name__ == "__main__":
    args = get_cli()
    runCombine.work_dir = args.workdir # same in all, so just set it

    card = f'{args.fit_var}_card.root'
    blindness = f'{args.blind} --expectSignal {args.r}'

    if need_redo_t2w(args.workdir, card):
        runCombine(f'text2workspace.py {card.replace("root", "txt")}')

    if args.type == "impact":
        runCombine(f'combineTool.py -M Impacts -d {card} -m 125 --doInitialFit --robustFit 1')
        runCombine(f'combineTool.py -M Impacts -d {card} -m 125 --robustFit 1 --doFits')
        runCombine(f'combineTool.py -M Impacts -d {card} -m 125 -o impacts.json')
        runCombine(f'plotImpacts.py -i impacts.json -o impacts')

    elif args.type == "sig":
        runCombine(f'combine -M Significance {card} {args.blind} --expectSignal 10  --toysFrequentist --freezeParameters allConstrainedNuisances')
        runCombine(f'combine -M Significance {card} {args.blind} --expectSignal 10  --toysFrequentist --freezeNuisanceGroups "syst_error"')
        runCombine(f'combine -M Significance {card} {args.blind} --expectSignal 10  --toysFrequentist ')

    elif args.type == "sig_scan":
        runCombine(f'combine -M Significance {card} {args.blind} --expectSignal 1  --toysFrequentist')
        runCombine(f'combine -M Significance {card} {args.blind} --expectSignal 1  --toysFrequentist --freezeParameters allConstrainedNuisances')
        for xsec in np.linspace(1, 100, 21):
            runCombine(f'combine -M Significance {card} {args.blind} --expectSignal {xsec} -m {xsec} --toysFrequentist --rMax 150 -n "_scan_all"')
            runCombine(f'combine -M Significance {card} {args.blind} --expectSignal {xsec} -m {xsec} --toysFrequentist --rMax 150 -n "_scan_frozen" --freezeNuisanceGroups "syst_error"')

        for sig_type in ["all", "frozen"]:
            sig_files = list(args.workdir.glob(f"higgsCombine_scan_{sig_type}*Significance*root"))
            subprocess.run(["hadd", "-f", args.workdir / f"significance_{sig_type}.root"] + sig_files)
            for sig_file in sig_files:
                sig_file.unlink()

        with plot(f"{args.workdir}/sig") as ax:
            with uproot.open(args.workdir / "significance_all.root") as f:
                df = f["limit"].arrays(library="pd")
                df = df.sort_values(by=["mh"])
                ax.scatter(df.mh, df.limit)
                ax.plot(df.mh, df.limit, label="Syst⊕Stat")
            with uproot.open(args.workdir / "significance_frozen.root") as f:
                df = f["limit"].arrays(library="pd")
                df = df.sort_values(by=["mh"])
                ax.scatter(df.mh, df.limit)
                ax.plot(df.mh, df.limit, label="Syst")
            ax.set_xlabel("ttt xsec multiplier")
            ax.set_ylabel("Significance")
            ax.legend()
            # ax.set_xscale("log")

    elif args.type == "asymtotic":
        runCombine(f'combine -M AsymptoticLimits {card} {blindness}')

    elif args.type == "hybrid":
        runCombine(f'combine -M HybridNew {card} {blindness} --LHCmod LHC-limits --saveHybridResult')
    elif args.type == "fit":
        runCombine(f'combine -M FitDiagnostics {card} {blindness} --rMin -20 --rMax 20')
    elif args.type == "help":
        runCombine("combine --help")
