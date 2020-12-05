import keras
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
import numpy as np
from source import Preprocess as pp
from collections import Counter
from models import DatasetHandler as dh
import sys
sys.path.append("../..")

class KerasModel:
    def __init__(self):
        self._preprocess = pp.Preprocess()
        self._model = keras.models.load_model('models/Saving/keras_model', )
        self._preprocess.set_dataset('datasets/Dataset.csv')
        self._x, self._y = self._preprocess.process_data_for_neural_with_label()
        self._train_size = 0.7
        self._metrics = [0.05013519152998924, 0.9858478903770447, 0.997950553894043]

    @property
    def model(self):
        return self._model

    @staticmethod
    def build_model(n_features, n_classes, num_layers=3):
        model = Sequential()
        delta = np.power(n_features / n_classes, 1 / num_layers)
        n_2 = np.int(4 * n_features / delta)
        n_3 = np.int(3 * n_2 / delta)
        model.add(Dense(n_2, input_dim=n_features, activation='relu'))
        model.add(Dense(n_3, activation='relu'))
        model.add(Dense(n_classes, activation='sigmoid'))
        return model

    def set_new_model(self, keras_model=""):
        if keras_model == '':
            raise IOError("No path to model")
        self._model = keras.models.load_model(keras_model)

    def set_pool(self, path_to_dataset=''):
        if path_to_dataset != '':
            self._preprocess.set_dataset(path_to_dataset)
            self._x, self._y = self._preprocess.process_data_for_neural_with_label()

    def get_predict_with_label(self, path_to_data=''):
        if path_to_data == '':
            raise IOError("No path to data")
        self._preprocess.set_dataset(path_to_data)
        self._x, self._y = self._preprocess.process_data_for_neural_with_label()
        return dh.massive(self._model.predict_classes(self._x))

    def relearn_model(self, path_to_dataset='', test_size=0.2):
        if path_to_dataset == '':
            raise IOError("No path to dataset")
        self.set_pool(path_to_dataset=path_to_dataset)
        self._train_size = 1 - test_size
        x_train, x_test, y_train, y_test = train_test_split(self._x, self._y, train_size=self._train_size)
        n_features = self._x.shape[1]
        n_cl = 1  # 2^1 =2
        self._model = KerasModel.build_model(n_features=n_features, n_classes=n_cl)
        self._model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'AUC'])
        self._model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=450, batch_size=10000)
        self._metrics = self._model.evaluate(x_test, y_test)

    def get_test_log_loss(self):
        return self._metrics[0]

    def get_test_accuracy(self):
        return self._metrics[1]

    def get_test_auc(self):
        return self._metrics[2]

    def get_predict_unknown(self, path_to_data=''):
        if path_to_data == '':
            raise IOError("No path to data")
        self._preprocess.set_dataset(path_to_data)
        self._x = self._preprocess.get_data_for_predict_neural()
        return dh.massive(self._model.predict_classes(self._x))


if __name__ == '__main__':
    k = KerasModel()
    c = Counter(k.get_predict_unknown('../datasets/imbalanced.csv'))
    print(c)
