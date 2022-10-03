import numpy as np

from .dataholder import MLHolder

class CutBasedMaker(MLHolder):
    def __init__(self, *args, **kwargs):
        """Constructor method
        """
        super().__init__(*args, **kwargs)
        self.cuts = kwargs.get("cuts")
        self.min_train_events = 1e10 # to not have train set

    def train(self, outdir):
        with open(f"{outdir}/cuts.txt", 'w') as f:
            for cut in self.cuts:
                f.write(f"{cut}\n")


    def predict(self, use_set, directory):
        self.get_cut_file(directory)
        signal = self._cut_mask(use_set)
        return np.array([[not i, i] for i in signal], dtype=float)

    def get_cut_file(self, workdir):
        self.cuts = [l.strip() for l in open(f"{workdir}/cuts.txt").readlines()]
