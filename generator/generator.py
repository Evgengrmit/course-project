"""
Принцип работы:
1. Считаем данные из csv для атаки (ddos_src.csv)
2. Выберем какой-нибудь комьютер (ip-адрес) источника атаки. В дальнейшем его будет выбирать
   пользователь в графическом интерфейсе
3. Выберем какой-нибудь комьютер из его списка жертв (поле Dst IP). В дальнейшем его будет выбирать
   пользователь в графическом интерфейсе
4. Сгенерируем пакеты для ddos атаки при помощи программы scapy
5. НЕ БУДЕМ!!! Никуда отправлять пакеты (мы не же хакеры, а просто учимся). Вместо
   Этого мы запишем информацию о пакетах в файлы .pcap - чтобы Вы могли на защите показать,
   что пакеты для атаки действительно формируются
6. Считаем данные из каждого .pcap файла (опять же библиотекой scapy)
7. Сгенерируем из этих данных о пакетах датасет в формате .csv, который Вы сможете "скормить"
   Вашей модели машинного обучения и нейронной сети
"""
import csv
# будем использовать для выбора из наших категориальных переменных пока случайных данных
# позже выбирать будет пользователь
import random as rd
from scapy.all import *
import collections as coll

Source_obj = coll.namedtuple('Source_obj',
                             ['source_ip', 'source_port', 'source_port', 'protocol', 'packets_count'])
Destination_obj = coll.namedtuple('Destination_obj',['dest_ip',])

class Generator:

    def __init__(self, path="", isSrc=False, isDst=False) -> None:
        self.path_ = path
        self.ddos_data_ = []
        self.source_ =
        self.source_data = Source_obj
        self.destination_ = Destination_obj
        if path != "":
            file = open(self.path_, "r")
            csv_reader = csv.DictReader(file, delimiter=",")
            for data in csv_reader:
                self.ddos_data_.append(data)
            file.close()
        if isSrc:
            source = rd.choice(self.ddos_data_)
            self.source_data.source_ip = source['Src IP']
            self.source_data.source_port = int(rd.choice(source['Src Port'].split(' ')))
            self.source_data.protocol = int(rd.choice(source['Protocol'].split(' ')))
            self.source_data.packets_count = int(float(source['Tot Fwd Pkts']))
        if isDst:

    # Шаг 1.
    def get_data(self, path=""):
        if path != "":
            self.path_ = path
            if path == "":
                raise IOError("Empty path")
            file = open(self.path_, "r")
            csv_reader = csv.DictReader(file, delimiter=",")
            for data in csv_reader:
                self.ddos_data_.append(data)
            file.close()
        return self.ddos_data_

    # Шаг 2.
    def get_random_source(self):
        source = rd.choice(self.ddos_data_)
        self.source_.source_ip = source['Src IP']
        self.source_.source_port = int(rd.choice(source['Src Port'].split(' ')))
        self.source_.protocol = int(rd.choice(source['Protocol'].split(' ')))
        self.source_.packets_count = int(float(source['Tot Fwd Pkts']))
        return self.source_

    # Шаг 3.
    def get_random_destination(self):
        dest_ip = rd.choice(source['Dst IP'].split(' '))
        dest_port = int(rd.choice(source['Dst Port'].split(' ')))

# Шаг 4.

packets = IP(src=source_ip, dst=dest_ip) / TCP(sport=source_port, dport=dest_port) / "TEST"

# Шаг 5.

pcap_filename = f"{source_ip}_{datetime.today().strftime('%d.%m.%Y')}.pcap"
wrpcap(pcap_filename, packets)

# Шаг 6.

readed_packers = rdpcap(pcap_filename)

print(readed_packers.show())
