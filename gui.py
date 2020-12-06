import PySimpleGUI as sg
from source import Detector as dt

import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")
sys.path.append("..")


def main():
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
            det = dt.Detector(name_of_model)
            det.find_in_unknown(path_to_data)
            print(det.results())
        if event in (None, 'Exit', 'Cancel'):
            break

if __name__ == '__main__':
    main()


