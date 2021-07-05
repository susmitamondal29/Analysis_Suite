#!/usr/bin/env python3

import os

os.environ["KERAS_BACKEND"] = "tensorflow"

import keras
from keras.backend import clear_session

from .dataholder import MLHolder

from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.model_selection import ShuffleSplit
from sklearn.utils import shuffle as shuffle_data
from sklearn.model_selection import cross_val_score

from dataclasses import dataclass, InitVar
import numpy as np

@dataclass
class Params:
    shuffle: bool = True
    initial_nodes: int = 10
    hidden_layers: int = 2
    node_pattern: str = "static"
    learning_rate: float = 0.01
    regulator: str = "dropout"
    activation: str = "elu"
    monitor: str = "loss"
    patience: int = 5
    mode: str = "auto"
    period: int = 1
    save_best_only: bool = True
    save_weights_only: bool = False
    epochs: int = 20
    batch_power: int = 9
    batch_size: int = 2**9
    validation_split: float = 0.25
    verbose: bool = False

    params: InitVar = None

    def __post_init__(self, params):
        if params is not None:
            for key, val in params.items():
                self.__setattr__(key, val)
            if "batch_power" in params:
                self.__setattr__("batch_size", params["batch_power"])

    def __getitem__(self, args):
        if isinstance(args, str):
            return {args: self.__getattribute__(args)}
        else:
            return {attr: self.__getattribute__(attr) for attr in args}


class KerasMaker(MLHolder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build = Params(params=kwargs.get("params"))

        self.params = self.build["epochs", "batch_size", "shuffle", "validation_split"]
        self.early_stop = self.build["monitor", "patience"]
        self.checkpoint = self.build["save_best_only", "save_weights_only", "mode", "period"]

    def build_model(self, input_size="auto"):
        node_lengths = self.build.initial_nodes * np.ones(
            self.build.hidden_layers, dtype=int
        )
        if self.build.node_pattern == "dynamic":
            partition = self.build.initial_nodes // self.build.hidden_layers
            node_lengths -= partition * np.arange(self.build.hidden_layers)

        # input_dim = len(self.use_vars) if input_size == "auto" else input_size
        model = keras.models.Sequential()
        model.add(
            keras.layers.core.Dense(
                self.build.initial_nodes,
                kernel_initializer="glorot_normal",
                input_dim=len(self.use_vars),
                activation=self.build.activation,
            )
        )

        for nodes in node_lengths:
            model.add(keras.layers.BatchNormalization())
            if self.build.regulator == "dropout":
                model.add(keras.layers.core.Dropout(0.5))
            model.add(
                keras.layers.core.Dense(
                    nodes,
                    kernel_initializer="glorot_normal",
                    activation=self.build.activation,
                )
            )

        # Final classification node
        model.add(keras.layers.core.Dense(1, activation="sigmoid"))
        model.compile(
            optimizer=keras.optimizers.Adam(lr=self.build.learning_rate),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        if self.build.verbose:
            model.summary()
        return model

    def train(self, outdir=""):
        shuf_train = self.train_set.sample(frac=1, random_state=0).reset_index(drop=True)

        signal = shuf_train[shuf_train["classID"] == 1]
        bkg = shuf_train[shuf_train["classID"] == 0]

        # print("BJETS")
        # print(np.histogram(signal["NBJets"], bins=np.arange(10)))
        # print(np.histogram(bkg["NBJets"], bins=np.arange(10)))
        # print()
        # print("JETS")
        # print(np.histogram(signal["NJets"], bins=np.arange(10)))
        # print(np.histogram(bkg["NJets"], bins=np.arange(10)))

        x_train = shuf_train.drop(self._drop_vars, axis=1)
        w_train = shuf_train["finalWeight"].to_numpy()
        y_train = shuf_train.classID
        
        x_test = self.test_set.drop(self._drop_vars, axis=1)
        y_test = self.test_set.classID

        _, group_tot = np.unique(y_train, return_counts=True)
        w_train[shuf_train["classID"] == 0] *= max(group_tot) / group_tot[0]
        w_train[shuf_train["classID"] == 1] *= max(group_tot) / group_tot[1]

        classW = {i: max(group_tot)/tot for i, tot in enumerate(group_tot)}
        callback = [
            keras.callbacks.EarlyStopping(**self.early_stop),
            # keras.callbacks.ModelCheckpoint("test.h5", verbose=0, **self.checkpoint),
        ]
        # Train
        print("\n>> Training.")
        fit_model = self.build_model()
        history = fit_model.fit(
            x_train, y_train.astype(bool),
            # sample_weight=w_train,
            class_weight= classW,
            callbacks=callback,
            verbose=self.build.verbose,
            **self.params
        )

        # Test
        print("\n>> Testing.")
        groupName = "Background"

        self.pred_test[groupName] = fit_model.predict(x_test).flatten()
        self.pred_train[groupName] = fit_model.predict(x_train).flatten()
        loss, accuracy = fit_model.evaluate(x_test, y_test, verbose=1)
        print(f'loss: {loss}')
        print(f'accuracy: {accuracy}')

        fpr_train, tpr_train, _ = roc_curve(y_train.astype(int), self.pred_train[groupName])
        fpr_test, tpr_test, _ = roc_curve(y_test.astype(int), self.pred_test[groupName])

        self.auc_train = auc(fpr_train, tpr_train)
        self.auc_test = auc(fpr_test, tpr_test)
        
        print(f'AUC for train: {self.auc_train}')
        print(f'AUC for test: {self.auc_test}')

        if outdir:
            fit_model.save(f'{outdir}/model.h5')

    def apply_model(self, directory, fit_test_vs_train=True):
        fit_model = keras.models.load_model(f'{directory}/model.h5')
        use_set = self.test_set if fit_test_vs_train else self.train_set
        pred = fit_model.predict(use_set.drop(self._drop_vars, axis=1))
        split_pred = {grp: (pred.T[i] if pred.shape[1] < i else 1 - pred.T[0])
                      for i, grp in enumerate(self.group_names)}
        if fit_test_vs_train:
            self.pred_test = split_pred
        else:
            self.pred_train = split_pred
