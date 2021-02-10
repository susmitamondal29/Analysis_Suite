#!/usr/bin/env python
import argparse
import pkg_resources as pkg
import xml.etree.ElementTree as ET

def writeHTML(path, name, channels=[]):
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
    info = ET.Element("Info")
    ET.SubElement(info, "Title").text = name
    for chan in channels:
        ET.SubElement(info, "Channel").text = chan
    tree = ET.ElementTree(info)
    tree.write('{}/extraInfo.xml'.format(path))

    for filename in pkg.resource_listdir(__name__, "../html"):
        print(filename)
        data = pkg.resource_string(__name__, "../html/{}".format(filename)).decode()
        with open("{}/{}".format(path, filename), 'w') as f:
            f.write(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path_to_files', type=str, required=True)
    parser.add_argument('-n', '--name', type=str, required=True)
    args = parser.parse_args()

    writeHTML(args.path_to_files.rstrip("/*"), args.name)
 
