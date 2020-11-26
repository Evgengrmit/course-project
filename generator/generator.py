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
                             ['source_ip', 'source_port', 'protocol', 'packets_count'])
Destination_obj = coll.namedtuple('Destination_obj', ['dest_ip', 'dest_port'])


class Generator:

    def __init__(self, path="", is_src=False, is_dst=False) -> None:
        self.path_ = path
        self.ddos_data_ = []
        self.source_ = None
        self.source_data = Source_obj
        self.destination_data = Destination_obj
        if path != "":
            file = open(self.path_, "r")
            csv_reader = csv.DictReader(file, delimiter=",")
            for data in csv_reader:
                self.ddos_data_.append(data)
            file.close()
        if is_src:
            self.source_ = rd.choice(self.ddos_data_)
            self.source_data.source_ip = self.source_['Src IP']
            self.source_data.source_port = int(rd.choice(self.source_['Src Port'].split(' ')))
            self.source_data.protocol = int(rd.choice(self.source_['Protocol'].split(' ')))
            self.source_data.packets_count = int(float(self.source_['Tot Fwd Pkts']))
        if is_dst:
            self.destination_data.dest_ip = rd.choice(self.source_['Dst IP'].split(' '))
            self.destination_data.dest_port = int(rd.choice(self.source_['Dst Port'].split(' ')))

    # Шаг 1.
    def get_data(self, path=""):
        if path != "":
            self.path_ = path
        else:
            raise IOError("Empty path")
        file = open(self.path_, "r")
        csv_reader = csv.DictReader(file, delimiter=",")
        for data in csv_reader:
            self.ddos_data_.append(data)
        file.close()
        return self.ddos_data_

    # Шаг 2.
    def get_random_source(self):
        self.source_ = rd.choice(self.ddos_data_)
        self.source_data.source_ip = self.source_['Src IP']
        self.source_data.source_port = int(rd.choice(self.source_['Src Port'].split(' ')))
        self.source_data.protocol = int(rd.choice(self.source_['Protocol'].split(' ')))
        self.source_data.packets_count = int(float(self.source_['Tot Fwd Pkts']))
        return self.source_

    # Шаг 3.
    def get_random_destination(self):
        self.destination_data.dest_ip = '.'.join('%s' % random.randint(0, 255) for i in range(4))
        # self.destination_data.dest_ip = rd.choice(self.source_['Dst IP'].split(' '))
        self.destination_data.dest_port = int(rd.choice(self.source_['Dst Port'].split(' ')))
        return self.destination_data

    # Шаг 4.
    def create_packet(self):
        packet_ = IP(src=self.source_data.source_ip, dst=self.destination_data.dest_ip) / TCP(
            sport=self.source_data.source_port, dport=self.destination_data.dest_port) / "TEST"
        return packet_

    # Шаг 5.
    def create_pcap(self, pack):
        pcap_filename = f"{self.source_data.source_ip}_{datetime.today().strftime('%d.%m.%Y')}.pcap"
        wrpcap(pcap_filename, pack)
        return pcap_filename


# Шаг 6.
if __name__ == '__main__':
    gen = Generator()
    gen.get_data("ddos_src.csv")
    gen.get_random_source()
    gen.get_random_destination()
    my_packet = gen.create_packet()
    readed_packets = rdpcap(gen.create_pcap(my_packet))
    print(readed_packets.show())
