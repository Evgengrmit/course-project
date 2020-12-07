from detector import KerasModel as ker
from detector import CatBoostModel as cat
from detector import LGBModel as lg
from models import DatasetHandler as dh
from collections import Counter
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class Detector:

    def __init__(self, model_name):
        self._model_name = model_name
        self._model = None
        if model_name == 'Keras':
            self._model = ker.KerasModel()
        elif model_name == 'CatBoost':
            self._model = cat.CatBoostModel()
        elif model_name == 'LightGBM':
            self._model = lg.LGBModel()
        else:
            raise IOError("No path to model")
        self._predicts = []
        self._count = {}

    def find_in_unknown(self, data_path):
        self._predicts = self._model.get_predict_unknown(data_path)
        return self._predicts

    def results(self):
        self._count = dict(Counter(self._predicts))
        self._count = dh.testKeras(self._model_name, self._count)
        res_str = f'{self._model_name}:\n'
        if len(self._count) == 2:
            res_str += f'DDoS objects: {self._count[1]}\n'
            res_str += f'Benign objects: {self._count[0]}\n'
        elif 0 in self._count:
            res_str += f'Benign objects: {self._count[0]}\n'
        elif 1 in self._count:
            res_str += f'DDoS objects: {self._count[1]}\n'
        return res_str
