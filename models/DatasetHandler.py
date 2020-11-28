"""
Function to prepare big Dataset
"""

import pandas as pd
import time
import datetime
import ipaddress
import seaborn as sns
import matplotlib.pyplot as plt


def get_small(path="", size=10, random_state=0):
    df = pd.read_csv(path)
    df.set_index([df.columns.values[0]], inplace=True)
    df.index.names = [None]
    small_benign = df.loc[df['Label'] == 'Benign'].sample(n=size, random_state=random_state)
    small_ddos = df.loc[df['Label'] == 'ddos'].sample(n=size, random_state=random_state)
    small_df = pd.concat([small_benign, small_ddos], ignore_index=True)
    small_df = small_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return small_df


def toTimestamp(strtime=""):
    timestamp = 0
    if strtime.find('AM') == -1 and strtime.find('PM') == -1:
        timestamp = time.mktime(datetime.datetime.strptime(strtime, "%d/%m/%Y %H:%M:%S").timetuple())
    else:
        timestamp = time.mktime(datetime.datetime.strptime(strtime, "%d/%m/%Y %H:%M:%S %p").timetuple())
    return timestamp


def iptodec(ip=""):
    return int(ipaddress.ip_address(ip))


def unique(df):
    nunique = df.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    df = df.drop(cols_to_drop, axis=1)
    return df


# Поиск коррелирующих признаков
def cormap(x_data, name=""):
    plt.figure(figsize=(55, 45))
    sns.heatmap(x_data.corr(), annot=True, cmap="RdBu")
    plt.title(name, fontsize=30)
    plt.plot()
    plt.savefig(f'images/{name}')


def plot_auc_array(data_array, tr_roc_auc, test_roc_auc):
    plt.figure(figsize=(14, 6))
    plt.plot(data_array, tr_roc_auc, label='train')
    plt.plot(data_array, test_roc_auc, label='test')
    plt.legend()
    plt.show()


def print_confusion_matrix(confusion_matrix, class_names, figsize = (10,7), fontsize=14):
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names,
    )
    fig = plt.figure(figsize=figsize)
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d",cmap="Blues")
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    return fig
