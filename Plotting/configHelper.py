import os
import time

from commons.configs import checkOrCreateDir

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
