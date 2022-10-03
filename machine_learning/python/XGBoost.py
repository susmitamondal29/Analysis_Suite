"""
.. module:: XGBoostMaker
   :synopsis: Takes in ROOT file to run a BDT training over it using XGBoost
.. moduleauthor:: Dylan Teague
"""
import numpy as np
import xgboost as xgb
from dataclasses import dataclass, InitVar, asdict

from .dataholder import MLHolder

def fom_metric(preds, dtrain):
    labels = dtrain.get_label()
    weights = dtrain.get_weight()

    maxfom = 0
    for cut in np.linspace(0, 1, 101):
        mask = preds > cut
        fom = np.sum(weights[mask*(labels==1)])/np.sqrt(np.sum(weights[mask]))
        maxfom = fom if fom > maxfom else maxfom
    return "fom", maxfom


@dataclass
class Params:
    eta: float = 0.09
    gamma: float = 0
    reg_alpha: float = 0.0
    min_child_weight: float = 1e-6
    n_estimators: float = 250
    reg_lambda: float = 0.05
    subsample: float = 1
    base_score: float = 0.5
    colsample_bylevel: int = 1
    colsample_bytree: int = 0.75
    learning_rate: float = 1
    max_depth: int = 3
    max_delta_step: int = 0
    objective: str = 'binary:logistic'
    eval_metric: str = "logloss"

    params: InitVar = None

    def __post_init__(self, params):
        if params is not None:
            for key, val in params.items():
                self.__setattr__(key, val)

    def __getitem__(self, args):
        if isinstance(args, str):
            return {args: self.__getattribute__(args)}
        else:
            return {attr: self.__getattribute__(attr) for attr in args}



class XGBoostMaker(MLHolder):
    def __init__(self, *args, **kwargs):
        """Constructor method
        """
        super().__init__(*args, **kwargs)

        self.param = Params(params=kwargs.get("params"))

    def update_params(self, params):
        self.param = Params(params=params)

    def train(self, outdir):
        """**Train for multiclass BDT**

        Does final weighting of the data (normalize all groups total
        weight to the same value), train the BDT, and fill the
        predictions ie the BDT values for each group.

        Returns:
          xgboost.XGBClassifer: XGBoost model that was just trained

        """
        x_train = self.train_set.drop(self._drop_vars, axis=1)
        w_train = self.train_set.train_weight.copy()
        y_train = self.train_set.classID

        x_test = self.validation_set.drop(self._drop_vars, axis=1)
        y_test = self.validation_set.classID
        w_test = self.validation_set.scale_factor

        _, group_tot = np.unique(y_train, return_counts=True)
        print(group_tot)
        w_train[self.train_set["classID"] == 0] *= max(group_tot)/group_tot[0]
        w_train[self.train_set["classID"] == 1] *= max(group_tot)/group_tot[1]

        fit_model = xgb.XGBClassifier(**asdict(self.param))
        fit_model.fit(x_train, y_train, sample_weight=w_train,
                      eval_set=[(x_train, y_train), (x_test, y_test)],
                      early_stopping_rounds=100, verbose=20)
        self.best_iter = fit_model.get_booster().best_iteration
        fit_model.save_model(f'{outdir}/model.bin')


    def predict(self, use_set, directory):
        fit_model = xgb.XGBClassifier({'nthread': 4})  # init model
        fit_model.load_model(str(directory / "model.bin"))  # load data
        return fit_model.predict_proba(use_set.drop(self._drop_vars, axis=1))

    def get_importance(self, directory):
        x_train = self.train_set.drop(self._drop_vars, axis=1)
        fit_model = xgb.XGBClassifier({'nthread': 4})  # init model
        fit_model.load_model(str(directory / "model.bin"))  # load data
        impor = fit_model.get_booster().get_score(importance_type= "total_gain")
        sorted_import = {x_train.columns[int(k[1:])]: v for k, v in sorted(impor.items(), key=lambda item: item[1]) }

        from analysis_suite.commons.plot_utils import plot, color_options
        with plot("{}/importance.png".format(directory)) as ax:
            ax.barh(range(len(sorted_import)), list(sorted_import.values()),
                    align='center',
                    height=0.5,)
            ax.set_yticks(range(len(sorted_import)))
            ax.set_yticklabels(sorted_import.keys())
            ax.set_xscale("log")
            ax.set_xlabel("Total Gain")
            ax.set_title("Variable Importance")

    def approx_likelihood(self, var, bins, year, comb_bkg=True):
        use_set = self.test_sets[year]

        sig_mask = use_set.classID.astype(int) == 1
        sig_wgt = use_set.scale_factor[sig_mask]
        sig_var = use_set[var][sig_mask]
        sig_pred = self.pred_test[year]["Signal"][sig_mask]

        bkg_mask = use_set.classID.astype(int) != 1
        bkg_wgt = use_set.scale_factor[bkg_mask]
        bkg_var = use_set[var][bkg_mask]
        bkg_pred = self.pred_test[year]["Signal"][bkg_mask]

        max_fom = [0, -1]
        for i in np.linspace(0, 1, 21):
            sig = np.histogram(sig_var[sig_pred > i], bins=bins, weights=sig_wgt[sig_pred > i])[0]
            bkg = np.histogram(bkg_var[bkg_pred > i], bins=bins, weights=bkg_wgt[bkg_pred > i])[0]
            value = np.sqrt(np.sum(2*np.nan_to_num((sig+bkg)*np.log(1+sig/bkg) - sig)))
            if max_fom[0] < value:
                max_fom = [value, i]
        return max_fom
