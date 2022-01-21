#!/usr/bin/env python3
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as clr
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
from contextlib import contextmanager

@contextmanager
def ratio_plot(filename, xlabel, binning):
    plot_inputs = {"nrows": 2, "ncols": 1, "sharex": True,
                   "gridspec_kw": {"hspace": 0.1, "height_ratios": [3,1]}}
    fig, ax = plt.subplots(**plot_inputs)
    yield ax
    setup_ticks(*ax)
    axisSetup(ax[0], ax[1], xlabel=xlabel, binning=binning)
    ax[0].legend()
    fig.tight_layout()
    if hasattr(plot, "workdir"):
        filename = f"{plot.workdir}/{filename}"
    fig.savefig(filename, bbox_inches="tight")
    plt.close(fig)



@contextmanager
def plot(filename, *args, **kwargs):
    fig, ax = plt.subplots(*args, **kwargs)
    yield ax
    fig.tight_layout()
    if hasattr(plot, "workdir"):
        filename = f"{plot.workdir}/{filename}"
    fig.savefig(filename, bbox_inches="tight")
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

def setup_ticks(pad, subpad=None):
    if subpad is not None:
        ticks(subpad)
        subpad.tick_params(direction="in")
    ticks(pad)


def ticks(pad):
    pad.minorticks_on()
    pad.tick_params(direction="in", length=9, top=True, right=True)
    pad.tick_params(direction="in", length=4, which='minor', top=True,
                    right=True)

def axisSetup(pad, subpad=None, xlabel="", binning=None, info=None):
    xpad = pad if subpad is None else subpad
    if xlabel:
        xpad.set_xlabel(xlabel)
    if binning is not None:
        xpad.set_xlim(binning)

    pad.set_ylim(bottom=0.)
    pad.set_ylabel("Events/bin")
    right_align_label(pad.get_yaxis(), isYaxis=True)
    right_align_label(xpad.get_xaxis())

    if subpad is not None:
        subpad.set_ylabel("Data/MC")
        subpad.set_ylim(top=2.0, bottom=0)

    # if info is not None:
    #     for key, val in info.items():
    #         getattr(xaxis, key)(val)

def right_align_label(axis, isYaxis=False):
    label = axis.get_label()
    if isYaxis:
        label.set_y(1.0)
    else:
        label.set_x(1.0)
    label.set_horizontalalignment('right')
    axis.set_label(label)
