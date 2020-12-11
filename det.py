# Copyright 2020 Evgenij Grigorev evgengrmit@icloud.com

import PySimpleGUI as sg
import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from detector.ddos_detector import Detector
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")


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
        if event == 'Submit':
            name_of_model = values[0]
            path_to_data = values['Browse']
            det = Detector(name_of_model)
            det.find_in_unknown(path_to_data)
            print(det.results())
        if event in (None, 'Exit', 'Cancel'):
            break


if __name__ == '__main__':
    main()
