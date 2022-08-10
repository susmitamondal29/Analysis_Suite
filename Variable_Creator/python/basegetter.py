#!/usr/bin/env python3
import numpy as np
from copy import copy

class BaseGetter:
    def __init__(self):
        self._mask = None
        self._scale = None

    def __bool__(self):
        return self._mask is not None

    def __len__(self):
        return np.count_nonzero(self.mask)

    def __getattr__(self, key):
        return self.__getitem__(key)


    @property
    def scale(self):
        return self._scale[self.mask]

    @scale.setter
    def scale(self, scale):
        if isinstance(scale, tuple):
            scale, mask = scale
            self._scale[self.get_submask(mask)] = scale
        else:
            self._scale[self.mask] = scale

    def get_submask(self, mask):
        submask = copy(self.mask)
        submask[submask] *= mask
        return submask

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        self._mask[self._mask] = mask * self._mask[self._mask]

    def clear_mask(self):
        self._mask = copy(self._base_mask)

    def cut(self, mask):
        self._base_mask[self._base_mask] = mask * self._base_mask[self._base_mask]
        self.clear_mask()

    def get_graph(self, graph):
        if graph.cuts is not None:
            self.mask = graph.cuts
        if callable(graph.func):
            return graph.func(self)
        else:
            return self.get_hist(graph.func)

    def get_hist(self, var):
        if not hasattr(self, var):
            raise AttributeError
        return self[var], self.scale
