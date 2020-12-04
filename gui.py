import PySimpleGUI as sg
layout = [
    [sg.Text(
    """
    What model you want to load?
    Please enter filename with model
    '.cbm' for CatBoost
    '. ...lgbm' for LightGBM
    '. ...nn' for Neural Network
    """), sg.InputText(), sg.FileBrowse()],
    [sg.Text('Enter filename of data'), sg.InputText(), sg.FileBrowse(),
     ],
    [sg.Output(size=(88, 20))],
    [sg.Submit(), sg.Cancel()]
]
window = sg.Window('File Compare', layout)
while True:                             # The Event Loop
    event, values = window.read()
    # print(event, values) #debug
    if event in (None, 'Exit', 'Cancel'):
        break
