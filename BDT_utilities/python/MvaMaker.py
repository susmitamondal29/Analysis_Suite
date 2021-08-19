"""
.. module:: XGBoostMaker
   :synopsis: Takes in ROOT file to run a BDT training over it using XGBoost
.. moduleauthor:: Dylan Teague
"""
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score, roc_curve, auc

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
        self.param = {"eta": 0.09, 'reg_alpha': 0.0,
                      'min_child_weight': 1e-6, 'n_estimators': 150,
                      'reg_lambda': 0.05,  'subsample': 1, 'base_score': 0.5,
                      'colsample_bylevel': 1, 'max_depth': 3, 'learning_rate': 0.1,
                      'colsample_bytree': 1, 'gamma': 0, 'max_delta_step': 0,}
        # 'silent': 1, 'scale_pos_weight': 1,

    def train(self, outdir):
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
        self.param['eval_metric'] = "auc"#"logloss"
        num_rounds = 150

        fit_model = xgb.XGBRegressor(**self.param)
        fit_model.fit(x_train, y_train, sample_weight=w_train,
                      eval_set=[(x_train, y_train), (x_test, y_test)],
                      early_stopping_rounds=25, verbose=50)
        
        groupName = "Background"
        self.pred_test[groupName] = fit_model.predict(x_test)
        self.pred_train[groupName] = fit_model.predict(x_train)

        fpr_train, tpr_train, _ = roc_curve(y_train.astype(int), self.pred_train[groupName])
        fpr_test, tpr_test, _ = roc_curve(y_test.astype(int), self.pred_test[groupName])

        auc_train = auc(fpr_train, tpr_train)
        auc_test = auc(fpr_test, tpr_test)

        print(f'AUC for train: {auc_train}')
        print(f'AUC for test: {auc_train}')

        fit_model.save_model(f'{outdir}/model.bin')


    def predict(self, use_set, directory):
        fit_model = xgb.XGBClassifier({'nthread': 4})  # init model
        fit_model.load_model(str(directory / "model.bin"))  # load data
        return fit_model.predict_proba(use_set.drop(self._drop_vars, axis=1))
