#!/usr/bin/env python3
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as clr

from contextlib import contextmanager

@contextmanager
def plot(filename, *args, **kwargs):
    fig, ax = plt.subplots(*args, **kwargs)
    yield ax
    fig.tight_layout()
    if hasattr(plot, "workdir"):
        filename = f"{plot.workdir}/{filename}"
    fig.savefig(filename)
    plt.close(fig)

def color_options(color):
    cvec = clr.to_rgb(color)
    dark = 0.3
    return {"color": color, "edgecolor": [i - dark if i > dark else 0.0 for i in cvec]}


def darkenColor(color):
    cvec = clr.to_rgb(color)
    dark = 0.3
    return [i - dark if i > dark else 0.0 for i in cvec]

def setup_mplhep():
    import mplhep as hep
    plt.style.use([hep.style.CMS, hep.style.firamath])
    return hep
