#!/usr/bin/env python3
import numpy as np

class Card_Maker:
    def __init__(self, path, channels, plot_groups, variable):
        self.variable = variable
        self.path = path
        self.years = channels
        self.channels = np.core.defchararray.add("yr", np.array(channels))
        self.plot_groups = np.array(plot_groups)
        self.nChans = len(self.channels)
        self.nGroups = len(self.plot_groups)

    def __enter__(self):
        self.f = open(f"{self.path}/{self.variable}_card.txt", 'w')
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()

    def tab_list(self, inlist):
        return  "\t" + "\t".join(inlist.astype(str))

    def write(self, line):
        self.f.write(line)
        self.f.write("\n")

    def end_section(self):
        self.write("-"*20)

    def write_systematics(self, syst_list):
        # Specify numbers of groups
        self.write(f"imax {self.nChans}  number of channels")
        self.write(f"jmax {self.nGroups - 1}  number of backgrounds plus signals minus 1")
        self.write(f"kmax {len(syst_list)} number of nuisance parameters (sources of systematical uncertainties)")
        self.end_section()

        # Specify shape locations
        self.write(f"shapes * * {self.path}/{self.variable}_$CHANNEL.root $PROCESS_Nominal $PROCESS_$SYSTEMATIC")
        self.end_section()

        # Specify channels and number of events
        self.write("bin" + self.tab_list(self.channels))
        self.write("observation" + self.tab_list(-1*np.ones(self.nChans)))
        self.end_section()

        # Specify channel and plot names with MC counts
        self.write("bin"+"".join(["\t{}".format(chan)*self.nGroups for chan in self.channels]))
        self.write("process"+ self.tab_list(self.plot_groups)*self.nChans)
        self.write("process"+ self.tab_list(np.arange(self.nGroups))*self.nChans)
        self.write("rate" + self.tab_list(-1*np.ones(self.nChans*self.nGroups)))
        self.end_section()

        # Specify systematics
        for syst in syst_list:
            self.write(syst.output(self.plot_groups, self.years))
        self.write("* autoMCStats 1")
