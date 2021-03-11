"""
.. module:: XGBoostMaker
   :synopsis: Takes in ROOT file to run a BDT training over it using XGBoost
.. moduleauthor:: Dylan Teague
"""
import numpy as np
import xgboost as xgb
from .dataholder import MLHolder

class XGBoostMaker(MLHolder):
    """Wrapper for XGBoost training. Takes an uproot input, a list of
    groups to do a multiclass training, as well as a cut string if
    needed and trains the data. After it is done, the results can be
    outputed to be piped into MVAPlotter

    Args:
      split_ratio(float): Ratio of test events for train test splitting
      group_names(list): List of the names of the different groups
      pred_train(dict): Dictionary of group name to BDT associated with it for train set
      pred_test(dict): Dictionary of group name to BDT associated with it for test set
      train_set(pandas.DataFrame): DataFrame of the training events
      test_set(pandas.DataFrame): DataFrame of the testing events
      cuts(list): List of ROOT style cuts to apply
      param(dict): Variables used in the training

    """
    def __init__(self, *args, **kwargs):
        """Constructor method
        """
        super().__init__(*args, **kwargs)
        self.param = {"eta": 0.09,  "nthread": 3, 'reg_alpha': 0.0,
                      'min_child_weight': 1e-6, 'n_estimators': 200,
                      'reg_lambda': 0.05,  'subsample': 1, 'base_score': 0.5,
                      'colsample_bylevel': 1, 'max_depth': 5, 'learning_rate': 0.1,
                      'colsample_bytree': 1, 'gamma': 0, 'max_delta_step': 0,}
        # 'silent': 1, 'scale_pos_weight': 1,

    def train(self):
        """**Train for multiclass BDT**

        Does final weighting of the data (normalize all groups total
        weight to the same value), train the BDT, and fill the
        predictions ie the BDT values for each group.

        Returns:
          xgboost.XGBClassifer: XGBoost model that was just trained

        """
        x_train = self.train_set.drop(self._drop_vars, axis=1)
        w_train = self.train_set["finalWeight"].copy()
        y_train = self.train_set["classID"]
        
        x_test = self.test_set.drop(self._drop_vars, axis=1)
        y_test = self.test_set["classID"]

        group_tot = [np.sum(w_train[self.train_set["classID"] == i]) for i in np.unique(y_train)]

        for i in np.unique(y_train):
            w_train[self.train_set["classID"] == i] *= max(group_tot)/group_tot[i]
            if i == self.group_names.index("Signal"):
                w_train[self.train_set["classID"] == i] *= 2

        self.param['objective'] = 'multi:softprob'
        self.param['eval_metric'] = "mlogloss"
        self.param['num_class'] = len(np.unique(y_train))

        fit_model = xgb.XGBClassifier(**self.param)
        fit_model.fit(x_train, y_train, w_train,
        eval_set=[(x_train, y_train), (x_test, y_test)],
                      early_stopping_rounds=100, verbose=50)

        for i, grp in enumerate(self.group_names):
            self.pred_test[grp] = fit_model.predict_proba(x_test).T[i]
            self.pred_train[grp] = fit_model.predict_proba(x_train).T[i]

        return fit_model

    def train_single(self):
        """**Train for multiclass BDT**

        Does final weighting of the data (normalize all groups total
        weight to the same value), train the BDT, and fill the
        predictions ie the BDT values for each group.

        Returns:
          xgboost.XGBClassifer: XGBoost model that was just trained

        """
        x_train = self.train_set.drop(self._drop_vars, axis=1)
        w_train = self.train_set["finalWeight"].copy()
        y_train = self.train_set.classID

        x_test = self.test_set.drop(self._drop_vars, axis=1)
        y_test = self.test_set.classID

        _, group_tot = np.unique(y_train, return_counts=True)
        w_train[self.train_set["classID"] == 0] *= max(group_tot)/group_tot[0]
        w_train[self.train_set["classID"] == 1] *= max(group_tot)/group_tot[1]

        self.param['objective'] = 'binary:logistic'
        self.param['eval_metric'] = "logloss"
        num_rounds = 150

        dtrain = xgb.DMatrix(x_train, label=y_train, weight=w_train)
        dtrainAll = xgb.DMatrix(self.train_set.drop(self._drop_vars, axis=1))
        dtest = xgb.DMatrix(x_test, label=y_test,
                            weight=self.test_set["finalWeight"])
        evallist = [(dtrain,'train'), (dtest, 'test')]
        fit_model = xgb.train(self.param, dtrain, num_rounds, evallist,
                              verbose_eval=50)

        groupName = "Background"#self.group_names[-1]
        self.pred_test[groupName] = fit_model.predict(dtest)
        self.pred_train[groupName] = fit_model.predict(dtrainAll)
        return fit_model

    def apply_model(self, model_file):
        fit_model = xgb.XGBClassifier({'nthread': 4})  # init model
        fit_model.load_model(model_file)  # load data

        for i, grp in enumerate(self.group_names):
            self.pred_test[grp] = fit_model.predict_proba(
                self.test_set.drop(self._drop_vars, axis=1)).T[i]
            self.pred_train[grp] = fit_model.predict_proba(
                self.train_set.drop(self._drop_vars, axis=1)).T[i]
        return fit_model

