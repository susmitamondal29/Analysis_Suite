import argparse
import os
import time
import awkward1 as ak
from histograms import Histogram
from commons.configs import checkOrCreateDir
import math

def getNormedHistos(indir, file_info, plot_info, histName, chan):
    groupHists = dict()
    ak_col = plot_info.Column[histName]
    for group, members in file_info.group2MemberMap.items():
        groupHists[group] = Histogram(file_info.get_legend_name(group),
                                      file_info.get_color(group),
                                      plot_info.get_binning(histName))
        for mem in members:
            narray = ak.Array({})
            try:
                array = ak.from_parquet("{}/{}.parquet".format(indir, mem),
                                        [ak_col, "scale_factor"])
            except:
                print("problem with {} getting histogram {}".format(mem, ak_col))
                continue
            sf = array["scale_factor"]
            vals = array[ak_col]
            if plot_info.Modify[histName]:
                vals = eval(plot_info.Modify[histName].format("vals"))
                if len(vals) != len(sf):
                    sf,_ = ak.unzip(ak.cartesian([sf, array[ak_col]]))
                    sf = ak.flatten(sf)
            narray[ak_col] = vals
            narray["scale_factor"] = sf
            #print("{}: {:.3f}+-{:.3f} ({})".format(mem, ak.sum(sf)*plot_info.lumi, plot_info.lumi*math.sqrt(ak.sum(sf)**2),len(sf)))
            groupHists[group] += narray

    for name, hist in groupHists.items():
        if file_info.lumi < 0:
            scale = 1 / sum(hist.hist)
            hist.scale(scale)
        else:
            hist.scale(plot_info.lumi)
    return groupHists

def setupPathAndDir(analysis, drawStyle, path, chans):
    """Setup HTML directory area and return path made"""
    extraPath = time.strftime("%Y_%m_%d")
    if path:
        extraPath = path + '/' + extraPath

    if 'hep.wisc.edu' in os.environ['HOSTNAME']:
        basePath = '{}/public_html'.format(os.environ['HOME'])
    elif 'uwlogin' in os.environ['HOSTNAME'] or 'lxplus' in os.environ['HOSTNAME']:
        basePath = '/eos/home-{0:1.1s}/{0}/www'.format(os.environ['USER'])
    basePath += '/PlottingResults/{}/{}_{}'.format(analysis, extraPath,
                                                   drawStyle)
    # for all directory
    checkOrCreateDir('{}/plots'.format(basePath))
    checkOrCreateDir('{}/logs'.format(basePath))
    for chan in chans:
        if "all": continue
        path = "{}/{}".format(basePath, chan)
        checkOrCreateDir(path)
        checkOrCreateDir('{}/plots'.format(path))
        checkOrCreateDir('{}/logs'.format(path))
    return basePath


import shutil


def copyDirectory(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)
