from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split
from source import Preprocess as pp
from sklearn.metrics import roc_auc_score, accuracy_score
from collections import Counter
import sys
sys.path.append("../..")

class CatBoostModel:
    def __init__(self):
        self._preprocess = pp.Preprocess()
        self._model = CatBoostClassifier()
        self._model.load_model("models/Saving/CBmodel.cbm")
        self._preprocess.set_dataset('datasets/Dataset.csv')
        self.x, self.y = self._preprocess.process_data_for_gradient_with_label()
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=0.3, random_state=42)
        self._train_data = Pool(x_train, y_train)
        self._test_data = Pool(x_test, y_test)

    @property
    def model(self):
        return self._model

    def set_new_model(self, cbm_model=""):
        if cbm_model == '':
            raise IOError("No path to model")
        self._model.load_model(cbm_model)

    def set_pool(self, path_to_dataset='', test_size=0.3):

        if path_to_dataset != '':
            self._preprocess.set_dataset(path_to_dataset)
            self.x, self.y = self._preprocess.process_data_for_gradient_with_label()

        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=test_size, random_state=42)
        self._train_data = Pool(x_train, y_train)
        self._test_data = Pool(x_test, y_test)

    def get_predict_with_label(self, path_to_data=''):
        if path_to_data == '':
            raise IOError("No path to data")
        self._preprocess.set_dataset(path_to_data)
        self.x, self.y = self._preprocess.process_data_for_gradient_with_label()
        return self._model.predict(self.x)

    def relearn_model(self, path_to_dataset='', test_size=0.3):
        if path_to_dataset == '':
            raise IOError("No path to dataset")
        self.set_pool(path_to_dataset=path_to_dataset, test_size=test_size)
        self._model = CatBoostClassifier(iterations=200,
                                         depth=2,
                                         learning_rate=0.4,
                                         loss_function='Logloss',
                                         verbose=False)
        self._model.fit(self._train_data, plot=True)

    def get_test_accuracy(self):
        return accuracy_score(self._test_data.get_label(), self._model.predict(self._test_data.get_features()))

    def get_test_auc(self):
        return roc_auc_score(self._test_data.get_label(),
                             self._model.predict_proba(self._test_data.get_features())[:, 1])

    def get_predict_unknown(self, path_to_data=''):
        if path_to_data == '':
            raise IOError("No path to data")
        self._preprocess.set_dataset(path_to_data)
        self.x = self._preprocess.get_data_for_predict_gradient()
        return self._model.predict(self.x)


if __name__ == '__main__':
    Cb = CatBoostModel()
    c = Counter(Cb.get_predict_unknown('../datasets/imbalanced.csv'))
    print(c)
