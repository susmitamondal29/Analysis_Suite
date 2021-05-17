from prettytable import PrettyTable
from pprint import pformat

import math
import numpy as np

BKG = 0
SIGNAL = 1
DATA = 2
TOTAL = 3

class LogFile:
    """Wrapper for Logfile for a plot

    Attributes
    ----------
    plotTable : PrettyTable
        PrettyTable holding all the histogram information
    output_name : string
        Name/path of logfile to be created
    analysis : string
        Analysis running over
    selection : string
        Selection of analysis running over
    lumi : float
        Luminosity of this run (in ipb, but converted to ifb in class)
    hists : list of lists
        List of lists with Integral and Error^2 indexed by the constants 
        BKG, SIGNAL, DATA, TOTAL
    callTime : string
        String of the time this script was called (any format)
    command : string
        Command used to start this script
    name : string
        Name of the histogram
    
    """
    callTime = ""
    command = ""
    def __init__(self, name, info, lumi, path='.'):
        self.plotTable = PrettyTable(["Plot Group", "Weighted Events", "Error"])
        self.breakTable = PrettyTable(["Plot Group", "Sample", "Weighted Events", "Error"])
        self.path = path
        self.output_name = f'{name}_info.log'
        self.analysis, self.selection = "", ""#info.getAnalysis()
        self.lumi = lumi
        self.hists = [np.array([0., 0.]) for i in range(4)] 
        self.hist_info = info
        self.name = name

    def add_mc(self, stacker):
        """Add background data to this class

        Parameters
        ----------
        drawOrder : list of tuples (string, GenericHist)
            List of all background hists with their names
        """
        for hist in stacker.stack:
            integral, error = hist.get_int_err(True)
            self.plotTable.add_row([hist.name, integral, error])
            self.hists[BKG] += hist.get_int_err()
        self.hists[TOTAL] += self.hists[BKG]

    def add_signal(self, signal):
        """Add signal data to this class

        Parameters
        ----------
        signal : GenericHist
            Histogram of signal information
        groupName : string
            Name used to label the singal
        """
        self.hists[SIGNAL] += signal.get_int_err()
        integral, error = signal.get_int_err(False)
        self.plotTable.add_row([signal.name, integral, error])
        self.hists[TOTAL] += self.hists[SIGNAL]

    @staticmethod
    def add_metainfo(callTime, command):
        """Set specific metadata for output file

        Parameters
        ----------
        callTime : string
            Time script was call (not formated, must be done before here)
        command : string
            Full commandline string use for this run

        """
        LogFile.callTime = callTime
        LogFile.command = command

    def get_sqrt_err(self, idx):
        """Grab the Integral and error on that information

        Parameters
        ----------
        idx : int
            int pointed to self.hists list
        """
        hist = self.hists[idx]
        hist[1] = np.sqrt(hist[1])
        return hist

    def write_out(self, isLatex=False):
        """Write out all current information to the objects output file

        Parameters
        ----------
        isLatex : bool, optional
            Whether table should be written out in latex or org style table
        """
        with open(f'{self.path}/{self.output_name}', 'w') as out:
            out.write("<html><pre><code>\n")
            out.write('-' * 80 + '\n')
            out.write(f'Script called at {LogFile.callTime} \n')
            out.write(f'The command was: {LogFile.command} \n')
            out.write(f'The name of this Histogram is: {self.name} \n')
            out.write('-' * 80 + '\n')
            out.write(f'Selection: {self.analysis,}/{self.selection}\n')
            out.write(f'Luminosity: {self.lumi:0.2f} fb^{{-1}}\n')
            if isLatex:
                out.write('\n' + self.plotTable.get_latex_string() + '\n'*2)
            else:
                out.write('\n' + self.plotTable.get_string() + '\n'*2)

            if self.hists[TOTAL].any():
                out.write("Total sum of Monte Carlo: {:0.2f} +/- {:0.2f} \n"
                             .format(*self.get_sqrt_err(TOTAL)))
            if self.hists[SIGNAL].any():
                out.write(
                    "Total sum of background Monte Carlo: {:0.2f} +/- {:0.2f} \n"
                    .format(*self.get_sqrt_err(BKG)))
                out.write("Ratio S/(S+B): {:0.2f} +/- {:0.2f} \n"
                          .format(*self.get_sig_bkg_ratio()))
                out.write("Ratio S/sqrt(S+B): {:0.2f} +/- {:0.2f} \n"
                          .format(*self.get_likelihood()))
            if self.hists[DATA].any():
                out.write(f'Number of events in data {self.hists[DATA][0]} \n')
            if isLatex:
                out.write('\n' + self.breakTable.get_latex_string() + '\n'*2)
            else:
                out.write('\n' + self.breakTable.get_string() + '\n'*2)
            out.write("\n" + pformat(self.hist_info))

            out.write("</code></pre></html>\n")


    def get_sig_bkg_ratio(self):
        """Get S/B with its error

        Returns
        -------
        tuple
            tuple S/B and its error
        """
        sig, sigErr = self.hists[SIGNAL]
        tot, totErr = self.hists[TOTAL]
        sigbkgd = sig / tot
        sigbkgdErr = sigbkgd * math.sqrt((sigErr / sig)**2 + (totErr / tot)**2)
        return (sigbkgd, sigbkgdErr)

    def get_likelihood(self):
        """Get Figure of merit

        Returns
        -------
        tuple
            tuple Figure of Merit (S/sqrt(S+B)) and its error
        """
        sig, sigErr = self.hists[SIGNAL]
        tot, totErr = self.hists[TOTAL]
        likelihood = sig / math.sqrt(tot)
        likelihoodErr = likelihood * math.sqrt((sigErr / sig)**2 +
                                               (0.5 * totErr / tot)**2)
        return (likelihood, likelihoodErr)

    def add_breakdown(self, group, break_dict):
        breakList = list()
        break_dict = {k: v for k, v in sorted(break_dict.items(), key=lambda item: item[1][1], reverse=True)}
        for sample, info in break_dict.items():
            events = round(info[0], 2)
            err = round(math.sqrt(info[1]), 2)
            self.breakTable.add_row([group, sample, events, err])
            group = ""
