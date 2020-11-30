import pandas as pd
from models import DatasetHandler as dh
from sklearn.preprocessing import MinMaxScaler


class Preprocess:
    name_of_features = {
        'Src Port',
        'Protocol',
        'Flow Duration',
        'Tot Fwd Pkts',
        'Tot Bwd Pkts',
        'Bwd Pkt Len Max',
        'Flow Byts/s',
        'Flow Pkts/s',
        'Flow IAT Mean',
        'Fwd PSH Flags',
        'Bwd PSH Flags',
        'Bwd Pkts/s',
        'FIN Flag Cnt',
        'SYN Flag Cnt',
        'URG Flag Cnt',
        'Down/Up Ratio',
        'Active Mean',
        'Idle Std',
        'Label'}

    def __init__(self, path='', name='', size=0, seed=0) -> None:
        self._path = path
        self._data = None
        self._name = name
        self._sizeOfBlock = size
        self._seed = seed
        self._obj = []
        self._labels = []

    def get_dataset(self, path='', size=0):
        if path == '' and self._path == '':
            raise IOError("Empty path")
        elif path != '':
            self._path = path
        if size == 0 and self._sizeOfBlock == 0:
            raise IOError("Zero size")
        elif size != 0:
            self._sizeOfBlock = size
        self._data = dh.get_small(self._path, self._sizeOfBlock, self._seed)
        return self._data

    def set_dataset(self, name=''):
        if name == '' and self._name == '':
            raise IOError("Empty path")
        elif name != '':
            self._name = name
        self._data = pd.read_csv(self._name, index_col=False)
        self._data = self._data.drop(columns=['Unnamed: 0'])
        return self._data

    def process_data_for_gradient(self):
        data_feat_set = set(self._data.columns.to_list())
        if not Preprocess.name_of_features.issubset(data_feat_set):
            raise IOError("There are no necessary attributes in the dataset")
        self._data['Label'] = self._data['Label'].replace("ddos", 1).replace("Benign", 0)
        drop_feat = data_feat_set - Preprocess.name_of_features
        self._data = self._data.drop(columns=list(drop_feat))
        self._labels = self._data['Label']
        self._obj = self._data.drop(columns='Label')
        return self._obj, self._labels

    def process_data_for_neural(self):
        Preprocess.process_data_for_gradient(self)
        self._obj, self._labels = dh.del_nan(self._obj, self._labels)
        sc = MinMaxScaler()
        self._obj = sc.fit_transform(self._obj)
        self._labels = self._labels.values
        return self._obj, self._labels

    def save_dataset(self, name=''):
        self._data.to_csv(name)

'''
if __name__ == '__main__':
    prep = Preprocess()
    #prep.get_dataset("/Users/evgenii/DDoS Dataset/final_dataset.csv", size=100)
    prep.set_dataset('datasets/Dataset.csv')
    X, y = prep.process_data_for_neural()
    print(X)

'''