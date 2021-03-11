#!/usr/bin/env python3

import os

os.environ["KERAS_BACKEND"] = "tensorflow"

import keras
from keras.backend import clear_session

from .dataholder import MLHolder

from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.model_selection import ShuffleSplit
from sklearn.utils import shuffle as shuffle_data

import numpy as np

# The parameters to apply to the cut.
SAVE_FPR_TPR_POINTS = 20


class Params:
    def __init__(self, indict):
        super(Params, self).__setattr__("dictionary", indict)

    def __getitem__(self, *args):
        if isinstance(args, str):
            keys = [args]  # args is a string
        else:
            keys = list(*args)  # args is a tuple
        return {key: self.dictionary[key] for key in keys}

    def __getattr__(self, item):
        return self.dictionary[item]


class KerasMaker(MLHolder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build = Params(
            {
                "initial_nodes": 50,
                "hidden_layers": 1,
                "node_pattern": "dynamic",
                # "node_pattern": "static",
                "lr": 1e-4,
                "regulator": "dropout",
                "activation": "tanh",
                "monitor": "val_loss",
                "patience": 5,
                "mode": "auto",
                "period": 1,
                "save_best_only": True,
                "save_weights_only": False,
                "epoch": 20,
                "batch_size": 2 ** 10,
                "shuffle": True,
                "validation_split": 0.25,
            }
        )
        self.params = self.build["epoch", "batch_size", "shuffle", "validation_split"]
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
            optimizer=keras.optimizers.Adam(lr=self.build.lr),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        model.summary()
        return model

    def train(self):
        x_train = self.train_set.drop(self._drop_vars, axis=1)
        w_train = self.train_set["finalWeight"].copy()
        y_train = self.train_set.classID

        x_test = self.test_set.drop(self._drop_vars, axis=1)
        y_test = self.test_set.classID

        _, group_tot = np.unique(y_train, return_counts=True)
        w_train[self.train_set["classID"] == 0] *= max(group_tot) / group_tot[0]
        w_train[self.train_set["classID"] == 1] *= max(group_tot) / group_tot[1]

        fit_model = self.build_model()
        callback = [
            keras.callbacks.EarlyStopping(**self.early_stop),
            keras.callbacks.ModelCheckpoint(verbose=0, **self.checkpoint),
        ]

        # Train
        print(">> Training.")
        history = self.model.fit(
            x_train, y_train, callbacks=callback, verbose=1, **self.params
        )

        # Test
        print(">> Testing.")
        groupName = "Background"
        self.pred_test[groupName] = fit_model.predict(x_test)
        self.pred_train[groupName] = fit_model.predict(x_train)

        print(self.pred_train[groupName])
        return fit_model

        # self.loss, self.accuracy = fit_model.evaluate(test_x, test_y, verbose=1)

        # self.fpr_train, self.tpr_train, _ = roc_curve(
        #     train_y.astype(int), model_ckp.predict(train_x)[:, 0]
        # )
        # self.fpr_test, self.tpr_test, _ = roc_curve(
        #     test_y.astype(int), model_ckp.predict(test_x)[:, 0]
        # )

        # self.auc_train = auc(self.fpr_train, self.tpr_train)
        # self.auc_test = auc(self.fpr_test, self.tpr_test)

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


# class CrossValidationModel( HyperParameterModel ):
#     def __init__( self, parameters, model_folder, num_folds = 5 ):
#         HyperParameterModel.__init__( self, parameters, None )
#         self.model_folder = model_folder
#         self.num_folds = num_folds
#         if not os.path.exists( self.model_folder ):
#             os.mkdir( self.model_folder )

#     def train_model( self ):
#         shuffle = ShuffleSplit( n_splits = self.num_folds, test_size = float( 1.0 / self.num_folds ), random_state = 0 )

#         # Set up and store k-way cross validation events
#         # Event inclusion masks
#         print( ">> Splitting events into {} sets for cross-validation.".format( self.num_folds ) )
#         fold_mask = {"signal": {}, "background": {}}

#         for path, events in self.cut_events[ "signal" ].iteritems():
#             self.cut_events[ "signal" ][path] = np.array(events)

#         for path, events in self.cut_events["background"].iteritems():
#             self.cut_events["background"][path] = np.array(events)

#         for path, events in self.cut_events["signal"].iteritems():
#             k = 0
#             fold_mask["signal"][path] = {}
#             for train, test in shuffle.split(events):
#                 fold_mask["signal"][path][k] = {"train": train, "test": test}
#                 k += 1

#         for path, events in self.cut_events["background"].iteritems():
#             k = 0
#             fold_mask["background"][path] = {}
#             for train, test in shuffle.split(events):
#                 fold_mask["background"][path][k] = {
#                     "train": train,
#                     "test": test
#                 }
#                 k += 1

#         # Event lists
#         fold_data = []
#         for k in range(self.num_folds):
#             sig_train_k = np.concatenate([
#                 self.cut_events["signal"][path][fold_mask["signal"][path][k]["train"]] for path in self.cut_events["signal"]
#             ])
#             sig_test_k = np.concatenate([
#                 self.cut_events["signal"][path][fold_mask["signal"][path][k]["test"]] for path in self.cut_events["signal"]
#             ])
#             bkg_train_k = np.concatenate([
#                 self.cut_events["background"][path][fold_mask["background"][path][k]["train"]] for path in self.cut_events["background"]
#             ])
#             bkg_test_k = np.concatenate([
#                 self.cut_events["background"][path][fold_mask["background"][path][k]["test"]] for path in self.cut_events["background"]
#             ])

#             fold_data.append( {
#                 "train_x": np.array( self.select_ml_variables(
#                   sig_train_k, bkg_train_k, self.parameters[ "variables" ] ) ),
#                 "test_x": np.array( self.select_ml_variables(
#                     sig_test_k, bkg_test_k, self.parameters[ "variables" ] ) ),

#                 "train_y": np.concatenate( (
#                   np.full( np.shape( sig_train_k )[0], 1 ).astype( "bool" ),
#                   np.full( np.shape( bkg_train_k )[0], 0 ).astype( "bool" ) ) ),
#                 "test_y": np.concatenate( (
#                     np.full( np.shape( sig_test_k )[0], 1 ).astype( "bool" ),
#                     np.full( np.shape( bkg_test_k )[0], 0 ).astype( "bool" ) ) )
#             } )

#         # Train each fold
#         print( ">> Beginning Training and Evaluation." )
#         self.model_paths = []
#         self.loss = []
#         self.accuracy = []
#         self.fpr_train = []
#         self.fpr_test = []
#         self.tpr_train = []
#         self.tpr_test = []
#         self.auc_train = []
#         self.auc_test = []
#         self.best_fold = -1

#         for k, events in enumerate(fold_data):
#             print("CV Iteration {} of {}".format(k + 1, self.num_folds))
#             keras.backend.clear_session()

#             model_name = os.path.join(self.model_folder, "fold_{}.h5".format(k))

#             self.build_model(events["train_x"].shape[1])

#             model_checkpoint = ModelCheckpoint(
#                 model_name,
#                 verbose=0,
#                 save_best_only=True,
#                 save_weights_only=False,
#                 mode="auto",
#                 period=1
#             )

#             early_stopping = EarlyStopping(
#                 monitor = "val_loss",
#                 patience=self.parameters[ "patience" ]
#             )

#             shuffled_x, shuffled_y = shuffle_data( events[ "train_x" ], events[ "train_y" ], random_state=0 )
#             shuffled_test_x, shuffled_test_y = shuffle_data( events[ "test_x" ], events[ "test_y" ], random_state=0 )

#             history = self.model.fit(
#                 shuffled_x, shuffled_y,
#                 epochs = self.parameters[ "epochs" ],
#                 batch_size = 2**self.parameters[ "batch_power" ],
#                 shuffle = True,
#                 verbose = 1,
#                 callbacks = [ early_stopping, model_checkpoint ],
#                 validation_split = 0.25
#             )

#             model_ckp = load_model(model_name)
#             loss, accuracy = model_ckp.evaluate(shuffled_test_x, shuffled_test_y, verbose=1)

#             fpr_train, tpr_train, _ = roc_curve( shuffled_y.astype(int), model_ckp.predict(shuffled_x)[:,0] )
#             fpr_test, tpr_test, _ = roc_curve( shuffled_test_y.astype(int), model_ckp.predict(shuffled_test_x)[:,0] )

#             auc_train = auc( fpr_train, tpr_train )
#             auc_test  = auc( fpr_test, tpr_test )

#             if self.best_fold == -1 or auc_test > max(self.auc_test):
#                 self.best_fold = k

#             self.model_paths.append( model_name )
#             self.loss.append( loss )
#             self.accuracy.append( accuracy )
#             self.fpr_train.append( fpr_train[ 0::int( len(fpr_train) / SAVE_FPR_TPR_POINTS ) ] )
#             self.tpr_train.append( tpr_train[ 0::int( len(tpr_train) / SAVE_FPR_TPR_POINTS ) ] )
#             self.fpr_test.append( fpr_test[ 0::int( len(fpr_test) / SAVE_FPR_TPR_POINTS ) ] )
#             self.tpr_test.append( tpr_test[ 0::int( len(tpr_test) / SAVE_FPR_TPR_POINTS ) ] )
#             self.auc_train.append( auc_train )
#             self.auc_test.append( auc_test )

#         print( "[OK ] Finished." )
