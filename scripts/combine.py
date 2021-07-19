#!/usr/bin/env python3
import subprocess
import argparse
from pathlib import Path

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
    parser.add_argument("type", type=str, choices=["impact"])
    parser.add_argument("-d", "--workdir", required=True, type=lambda x : Path(x)/"combine",
                        help="Working Directory")
    parser.add_argument("-f", "--fit_var", required=True,
                        help="Variable used for fitting")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_cli()
    runCombine.work_dir = args.workdir # same in all, so just set it

    card = f'{args.fit_var}_card.txt'

    if args.type == "impact":
        runCombine(f'text2workspace.py {card}')
        card_root = f'{args.fit_var}_card.root'
        runCombine(f'combineTool.py -M Impacts -d {card_root} -m 125 --doInitialFit --robustFit 1')
        runCombine(f'combineTool.py -M Impacts -d {card_root} -m 125 --robustFit 1 --doFits')
        runCombine(f'combineTool.py -M Impacts -d {card_root} -m 125 -o impacts.json')
        runCombine(f'plotImpacts.py -i impacts.json -o impacts')

    # runCombine(f"combine -M AsymptoticLimits {card_root}")
