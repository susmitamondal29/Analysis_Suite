from analysis_suite.commons.histogram import Histogram
from analysis_suite.commons.plot_utils import darkenColor

import numpy as np

class Stack(Histogram):
    def __init__(self, bin_info):
        super().__init__("", bin_info)
        self.stack = list()
        self.options = {"stacked": True, "histtype": "stepfilled"}

    def __iadd__(self, right):
        idx = self._get_index(right.integral())
        self.stack.insert(idx, right)
        return super().__iadd__(right)

    def _get_index(self, integral):
        if not self.stack:
            return 0
        else:
            return np.argmax(np.array([s.integral() for s in self.stack]) < integral)

    def applyPatches(self, patches):
        edgecolors = [darkenColor(h.color) for h in self.stack]
        for p, ec in zip(patches, edgecolors):
            p[0].set_ec(ec)

    def getInputs(self, **kwargs):
        stack = [h.vals for h in self.stack]
        base_vals = [self.axis.centers for _ in range(len(stack))]
        fancyNames = [h.name for h in self.stack]
        colors = [h.color for h in self.stack]
        rDict = dict({"weights": stack, "bins": self.axis.edges,
                      "x": base_vals, "color": colors, "label": fancyNames,
                      }, **self.options)
        rDict.update(kwargs)
        return rDict

#     def setDrawType(self, drawtype):
#         if drawtype == "compare":
#             self.options["stacked"] = False
#             self.options["histtype"] = "step"
#             self.edgecolors = self.colors
