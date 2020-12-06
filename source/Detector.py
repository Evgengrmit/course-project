from source import KerasModel as ker
from source import CatBoostModel as cat
from source import LGBModel as lg
from collections import Counter
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
sys.path.append("..")


class Detector:

    def __init__(self, model_name) -> None:
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
        res_str = f'{self._model_name}:\n'
        res_str += f'DDoS objects: {self._count[1]}\n'
        res_str += f'Benign objects: {self._count[0]}'
        return res_str
