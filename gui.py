import PySimpleGUI as sg

from source import KerasModel as ker, CatBoostModel as cat, LGBModel as lg
from collections import Counter
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
sys.path.append("..")

class Detector:

    def __init__(self, model_name) -> None:
        self._model = None
        if model_name == 'Keras':
            self._model = ker.KerasModel()
        elif model_name == 'CatBoost':
            self._model = cat.CatBoostModel()
        elif model_name == 'LightGBM':
            self._model = lg.LGBModel()
        else:
            raise IOError("No path to model")

    def find_in_unknown(self, data_path):
        return self._model.get_predict_unknown(data_path)




layout = [
    [sg.Text('Select  model'), sg.InputCombo(['Keras', 'CatBoost', 'LightGBM'])],
    [sg.Text('Select file with data'), sg.FileBrowse()],
    [sg.Output(size=(88, 20))],
    [sg.Submit(), sg.Cancel()]
]
window = sg.Window('Detect DDoS', layout)
while True:  # The Event Loop
    event, values = window.read()
    if event == 'Submit':
        name_of_model = values[0]
        path_to_data = values['Browse']
        det = Detector(name_of_model)
        print(Counter(det.find_in_unknown(path_to_data)))
    if event in (None, 'Exit', 'Cancel'):
        break



