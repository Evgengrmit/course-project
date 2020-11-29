
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import pandas as pd
print(1)

str_hello = """
        What model you want to load?
        Please type
        '1' for CatBoost
        '2' for LightGBM
        '3' for Neural Network
        """
str_wrong_num = "Wrong number for model"


data_file = 'datasets/Dataset.csv'
cbm_file  = '../Downloads/cat_boost.cbm'

def data_preproc_boost(df):
    y = df['Label'].values
    x = df.drop(columns=['Unnamed: 0', 'Label']).values

    return x, y


def ex_catboost():
    model = CatBoostClassifier()
    model.load_model(cbm_file)
    df = pd.read_csv(data_file)
    x, y = data_preproc_boost(df)

    preds = model.predict(x)
    ac = accuracy_score(preds, y)

    print(ac)

    exit()


if __name__ == "__main__":

    print(str_hello)
    model = False
    num_model = int(input())

    while not model:
        model = True
        if num_model == 1:
            ex_catboost()
        elif num_model == 2:
            pass
        elif num_model == 3:
            pass
        else:
            print(str_wrong_num)
            model = False
