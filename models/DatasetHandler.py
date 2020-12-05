"""
Function to prepare big Dataset
"""

import numpy as np
import pandas as pd
import time
import datetime
import ipaddress
import seaborn as sns
import matplotlib.pyplot as plt


def get_balanced(path='', size=10, random_state=0):
    if size % 2:
        raise IOError('The number of elements must be even')
    df = pd.read_csv(path)
    df.set_index([df.columns.values[0]], inplace=True)
    df.index.names = [None]
    small_benign = df.loc[df['Label'] == 'Benign'].sample(n=int(size / 2), random_state=random_state)
    small_ddos = df.loc[df['Label'] == 'ddos'].sample(n=int(size / 2), random_state=random_state)
    small_df = pd.concat([small_benign, small_ddos], ignore_index=True)
    small_df = small_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return small_df


def get_imbalanced(path='', size=10, ddos=0.3, benign=0.7, random_state=20):
    if int(ddos + benign) != 1:
        raise IOError('ddos+benign != 1')
    df = pd.read_csv(path)
    df.set_index([df.columns.values[0]], inplace=True)
    df.index.names = [None]
    small_benign = df.loc[df['Label'] == 'Benign'].sample(n=int(size * benign), random_state=random_state)
    small_ddos = df.loc[df['Label'] == 'ddos'].sample(n=int(size * ddos), random_state=random_state)
    small_df = pd.concat([small_benign, small_ddos], ignore_index=True)
    small_df = small_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return small_df


def toTimestamp(strtime=""):
    timestamp = 0
    if strtime.find('AM') == -1 and strtime.find('PM') == -1:
        timestamp = time.mktime(datetime.datetime.strptime(strtime, '%d/%m/%Y %H:%M:%S').timetuple())
    else:
        timestamp = time.mktime(datetime.datetime.strptime(strtime, '%d/%m/%Y %H:%M:%S %p').timetuple())
    return timestamp


def iptodec(ip=""):
    return int(ipaddress.ip_address(ip))


def unique(df):
    nunique = df.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    df = df.drop(cols_to_drop, axis=1)
    return df


# Поиск коррелирующих признаков
def cormap(x_data, name=''):
    plt.figure(figsize=(55, 45))
    sns.heatmap(x_data.corr(), annot=True, cmap='RdBu')
    plt.title(name, fontsize=30)
    plt.plot()
    plt.savefig(f'images/{name}')


def plot_auc_array(data_array, tr_roc_auc, test_roc_auc):
    plt.figure(figsize=(14, 6))
    plt.plot(data_array, tr_roc_auc, label='train')
    plt.plot(data_array, test_roc_auc, label='test')
    plt.legend()
    plt.show()


def print_confusion_matrix(confusion_matrix, class_names, figsize=(10, 7), fontsize=14):
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names,
    )
    fig = plt.figure(figsize=figsize)
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt='d', cmap='Blues')
    except ValueError:
        raise ValueError('Confusion matrix values must be integers.')
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    return fig


def show_nn_metrics(history):
    plt.figure(figsize=(20, 37))
    plt.subplot(3, 1, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(history.history['auc'])
    plt.plot(history.history['val_auc'])
    plt.title('Model AUC')
    plt.ylabel('AUC')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.grid(True)


def del_nan_data(x):
    msk = ~x.isin([np.nan, np.inf, -np.inf]).any(1)
    x = x[msk]
    return x


def del_nan_with_label(x, y):
    msk = ~x.isin([np.nan, np.inf, -np.inf]).any(1)
    x = del_nan_data(x)
    y = y[msk]
    return x, y
