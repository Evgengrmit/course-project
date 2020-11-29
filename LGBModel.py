import lightgbm as lgb
from sklearn.model_selection import train_test_split
import Preprocess as pp
from sklearn.metrics import roc_auc_score, accuracy_score
import warnings

warnings.filterwarnings('ignore')


def set_parameters():
    param_ = {'boosting_type': 'gbdt',
              'objective': 'binary',
              'metric': 'binary_logloss',
              'learning_rate': 0.4,
              'num_threads': -1,
              'max_depth': 2,
              'verbose': -1,
              'num_leaves': 8}
    return param_


class LGBModel:
    def __init__(self):
        self._preprocess = pp.Preprocess()
        self._model = lgb.Booster(model_file='models/Saving/lgbm_model.mdl')
        self.parameters = set_parameters()
        self._preprocess.set_dataset('datasets/Dataset.csv')
        self.x, self.y = self._preprocess.process_data_for_gradient()
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=0.3, random_state=42)
        self._train_data = lgb.Dataset(x_train, label=y_train, free_raw_data=False).construct()
        self._test_data = lgb.Dataset(x_test, label=y_test, reference=self._train_data, free_raw_data=False).construct()

    def set_new_model(self, lgb_model=""):
        if lgb_model == '':
            raise IOError("No path to model")
        self._model = lgb.Booster(model_file=lgb_model)

    def set_lgb_dataset(self, path_to_dataset='', test_size=0.3):
        if path_to_dataset != '':
            self._preprocess.set_dataset(path_to_dataset)
            self.x, self.y = self._preprocess.process_data_for_gradient()
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=test_size, random_state=42)
        self._train_data = lgb.Dataset(x_train, label=y_train, free_raw_data=False)
        self._test_data = lgb.Dataset(x_test, label=y_test, reference=self._train_data, free_raw_data=False)

    def get_predict(self, path_to_data=''):
        if path_to_data == '':
            raise IOError("No path to data")
        self._preprocess.set_dataset(path_to_data)
        self.x, self.y = self._preprocess.process_data_for_gradient()
        return self._model.predict(self.x).round(0)

    def relearn_model(self, path_to_dataset='', test_size=0.3):
        if path_to_dataset == '':
            raise IOError("No path to dataset")
        self.set_lgb_dataset(path_to_dataset=path_to_dataset, test_size=test_size)
        self.parameters = set_parameters()
        self._model = lgb.train(self.parameters, self._train_data, 200, valid_sets=self._test_data, verbose_eval=False)

    def get_test_accuracy(self):
        return accuracy_score(self._test_data.get_label(), self._model.predict(self._test_data.get_data()).round(0))

    def get_test_auc(self):
        return roc_auc_score(self._test_data.get_label(),
                             self._model.predict(self._test_data.get_data()))


'''
if __name__ == '__main__':
    lg = LGBMmodel()
    lg.relearn_model('datasets/Test.csv', 0.3)
    print(lg.get_test_auc())
    print(lg.get_test_accuracy())
    print(lg.get_predict('datasets/Dataset.csv'))
'''
