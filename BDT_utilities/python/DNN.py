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

import numpy as np

# The parameters to apply to the cut.
SAVE_FPR_TPR_POINTS = 20


class Params:
    def __init__(self, indict):
        super(Params, self).__setattr__("dictionary", indict)

    def __getitem__(self, *args):
        if isinstance(*args, str):
            keys = [args[0]]  # args is a string
        else:
            keys = list(*args)  # args is a tuple
        return {key: self.dictionary[key] for key in keys if key in self.dictionary}

    def __getattr__(self, item):
        return self.dictionary[item]

    def __setattr__(self, name, value):
        self.dictionary[name] = value

    def update(self, new):
        self.dictionary.update(new)

class KerasMaker(MLHolder):
    def __init__(self, *args, params={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.build = Params(
            {
                #"shuffle": True,
                "initial_nodes": 20,
                "hidden_layers": 1,
                "node_pattern": "dynamic",
                "learning_rate": 0.01,
                "regulator": "dropout",
                "activation": "elu",
                "monitor": "val_loss",
                "patience": 5,
                "mode": "auto",
                "period": 1,
                "save_best_only": True,
                "save_weights_only": False,
                "epochs": 1,
                "batch_power": 10,
                "validation_split": 0.25,
                "verbose": False,
            }
        )
        self.build.update(params)
        self.build.batch_size = 2**self.build.batch_power
        
        self.params = self.build["epochs", "batch_size", "shuffle", "validation_split"]
        self.early_stop = self.build["monitor", "patience"]
        self.checkpoint = self.build[
            "save_best_only", "save_weights_only", "mode", "period"
        ]

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
        print(shuf_train.to_string())
        signal = shuf_train[shuf_train["classID"] == 1]
        bkg = shuf_train[shuf_train["classID"] == 0]

        print("BJETS")
        print(np.histogram(signal["NBJets"], bins=np.arange(10)))
        print(np.histogram(bkg["NBJets"], bins=np.arange(10)))
        print()
        print("JETS")
        print(np.histogram(signal["NJets"], bins=np.arange(10)))
        print(np.histogram(bkg["NJets"], bins=np.arange(10)))

        x_train = shuf_train.drop(self._drop_vars, axis=1)
        w_train = shuf_train["finalWeight"].to_numpy()
        y_train = shuf_train.classID
        exit()
        x_test = self.test_set.drop(self._drop_vars, axis=1)
        y_test = self.test_set.classID

        _, group_tot = np.unique(y_train, return_counts=True)
        w_train[shuf_train["classID"] == 0] *= max(group_tot) / group_tot[0]
        w_train[shuf_train["classID"] == 1] *= max(group_tot) / group_tot[1]
        print(group_tot)


        classW = {i: max(group_tot)/tot for i, tot in enumerate(group_tot)}
        callback = [
            keras.callbacks.EarlyStopping(**self.early_stop),
            # keras.callbacks.ModelCheckpoint("test.h5", verbose=0, **self.checkpoint),
        ]
        
        # Train
        print(">> Training.")
        fit_model = self.build_model()
        history = fit_model.fit(
            x_train, y_train.astype(bool),
            # sample_weight=w_train,
            # class_weight= classW,
            callbacks=callback,
            verbose=self.build.verbose,
            **self.params
        )

        # Test
        print(">> Testing.")
        groupName = "Background"

        self.pred_test[groupName] = fit_model.predict(x_test).flatten()
        self.pred_train[groupName] = fit_model.predict(x_train).flatten()
        # print(fit_model.predict(x_train))
        # print(x_train)
        # loss, accuracy = fit_model.evaluate(x_test, y_test, verbose=1)
        # print("loss: {}".format(loss))
        # print("accuracy: {}".format(accuracy))
        print(y_train.to_numpy(dtype=int))
        print(self.pred_train[groupName])
        ftrain, ttrain, _ = roc_curve(y_train.astype(int), self.pred_train[groupName])
        print(ftrain)
        print(ttrain)
        print(auc(ftrain, ttrain))


        fpr_train, tpr_train, _ = roc_curve(y_train.astype(int), self.pred_train[groupName])
        fpr_test, tpr_test, _ = roc_curve(y_test.astype(int), self.pred_test[groupName])

        self.auc_train = auc(fpr_train, tpr_train)
        self.auc_test = auc(fpr_test, tpr_test)
        
        print("AUC for train: {}".format(self.auc_train))
        print("AUC for test: {}".format(self.auc_test))
        exit()
        # fit_model.save("{}/model.h5".format(outdir))


    def apply_model(self, model_file):
        fit_model = keras.models.load_model(model_file)
        for i, grp in enumerate(self.group_names):
            self.pred_test[grp] = fit_model.predict(
                self.test_set.drop(self._drop_vars, axis=1)
            ).T[i]
            self.pred_train[grp] = fit_model.predict(
                self.train_set.drop(self._drop_vars, axis=1)
            ).T[i]
        return fit_model


