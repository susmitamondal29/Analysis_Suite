#!/usr/bin/env python
import argparse
import pkg_resources as pkg
import json
from pathlib import Path

def writeHTML(path, name, subdir=[]):
    """**Creates a useable HTML page of plots**
    
    Copies the necessary files (located in the html directory)

    Parameters
    ----------
    path : string
        Where the files should be saved
    name : string
        Name of the analysis used for titling
    channels : list of strings, optional
        List of channels to create the differnt sub-webpages
    """
    needWrite = False
    for filename in pkg.resource_listdir(__name__, "../html"):
        # if (path / filename).exists():
        #     continue
        needWrite = True
        data = pkg.resource_string(__name__, f'../html/{filename}').decode()
        with open(f'{path}/{filename}', 'w') as f:
            f.write(data)
    if not needWrite:
        return
    info = { "Title" : name,
             "Subdirectory" : subdir}
    with open(f'{path}/extraInfo.json', 'w') as outjson:
        outjson.write(json.dumps(info))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path_to_files', type=str, required=True)
    parser.add_argument('-n', '--name', type=str, required=True)
    args = parser.parse_args()

    writeHTML(args.path_to_files.rstrip("/*"), args.name)
 
