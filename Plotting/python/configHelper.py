import os
import time

from analysis_suite.commons.configs import checkOrCreateDir

def setupPathAndDir(analysis, drawStyle, path, chans):
    """Setup HTML directory area and return path made"""

    extraPath = time.strftime("%Y_%m_%d")
    if path:
        extraPath = path + '/' + extraPath

    if 'hep.wisc.edu' in os.environ['HOSTNAME']:
        basePath = f'{os.environ["HOME"]}/public_html'
    elif 'uwlogin' in os.environ['HOSTNAME'] or 'lxplus' in os.environ['HOSTNAME']:
        basePath = '/eos/home-{0:1.1s}/{0}/www'.format(os.environ['USER'])
    basePath += f'/PlottingResults/{analysis}/{extraPath}_{drawStyle}'
    # for all directory
    checkOrCreateDir(f'{basePath}/plots')
    checkOrCreateDir(f'{basePath}/logs')

    for chan in chans:
        path = f'{basePath}/{chan}'
        checkOrCreateDir(path)
        checkOrCreateDir(f'{path}/plots')
        checkOrCreateDir(f'{path}/logs')
    return basePath
