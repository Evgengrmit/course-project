import PySimpleGUI as sg
from source import Detector as dt

import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
sys.path.append("..")


def main():
    layout = [
        [sg.Text('Выберите модель'), sg.InputCombo(['Keras', 'CatBoost', 'LightGBM'])],
        [sg.Text('Выберите файл'), sg.FileBrowse()],
        [sg.Output(size=(88, 20))],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Детектор DDoS-атаки', layout)
    while True:  # The Event Loop
        event, values = window.read()
        if event == 'Начать':
            name_of_model = values[0]
            path_to_data = values['Browse']
            det = dt.Detector(name_of_model)
            det.find_in_unknown(path_to_data)
            print(det.results())
        if event in (None, 'Exit', 'Cancel'):
            break


if __name__ == '__main__':
    main()
''' 
det = dt.Detector('Keras')
 det.find_in_unknown('/Users/evgenii/Downloads/generator/attack_data/generated_result_06.12.2020_15-32-19.csv')
 print(det.results())
'''
