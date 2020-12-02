import csv
import random
import datetime
import os, sys, math, copy
from scapy.all import *
import numpy as np
# Шаг 1. Считываем данные из файла с атаками ddos_src.csv
print('Загружаем данные базового датасета...')
file = open("ddos_src.csv", "r")
csv_reader = csv.DictReader(file, delimiter=",")

ddos_data = []

for data in csv_reader:
    ddos_data.append(data)

ports = ddos_data[0]['Src Port'].split(" ")
file.close()

# Шаг 2. Выбираем бота (комьпютер-источник атаки)

source = random.choice(ddos_data)

source_ip = source['Src IP']
source_port = int(random.choice(source['Src Port'].split(' ')))
protocol = int(random.choice(source['Protocol'].split(' ')))
packets_count = int(float(source['Tot Fwd Pkts']))

# Шаг 3. Выбираем компьютер жертву
dest_ip = random.choice(source['Dst IP'].split(' '))
dest_port = int(random.choice(source['Dst Port'].split(' ')))

# Шаг 4. Генерируем пакеты для атаки

# Шаг 5. Сохраняем сгенерированный пакет/пакеты в файл .pcap


dest_ip = input("Введите ip-адрес жертвы: ")

dest_ports = map(int, input("Укажите через пробел атакуемые порты (80/443): ").split(' '))

attack_time = int(input("Укажите время атаки в секундах: "))

bots_count = random.randint(5, len(ddos_data))

ddos_packets = {}

start_timestamp = datetime.now().timestamp()

current_timestamp = start_timestamp

print('Генерируем сетевые пакеты...')

dest_ports = list(dest_ports)

while current_timestamp < start_timestamp + attack_time:

    for i in range(bots_count):
        time_duration = 1
        source = random.choice(ddos_data)
        source_ip = source['Src IP']
        source_port = int(random.choice(source['Src Port'].split(' ')))
        protocol = int(random.choice(source['Protocol'].split(' ')))
        packets_count = float(source['Tot Fwd Pkts'])
        data = random._urandom(1024)

        flags = ''
        # Устанавливаем различные флаги случайным образом
        if protocol == 6:
            transport_protocol = TCP(sport=source_port, dport=dest_ports)
            print(source_ip, float(source['SYN Flag Cnt']) * packets_count, packets_count)
            if 'SYN Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['SYN Flag Cnt']) * packets_count:
                flags += 'S'

            if 'ACK Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['ACK Flag Cnt']) * packets_count:
                flags += 'A'

            if 'RST Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['RST Flag Cnt']) * packets_count:
                flags += 'R'

            if 'URG Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['URG Flag Cnt']) * packets_count:
                flags += 'U'

            if 'FIN Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['FIN Flag Cnt']) * packets_count:
                flags += 'F'

            if 'CWE Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['CWE Flag Cnt']) * packets_count:
                flags += 'C'

            if 'ECE Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['ECE Flag Cnt']) * packets_count:
                flags += 'E'

            if 'PSH Flag Cnt' in source and random.uniform(0, packets_count) <= float(
                    source['PSH Flag Cnt']) * packets_count:
                flags += 'P'
        else:
            transport_protocol = UDP(dport=dest_ports)

        if source_ip not in ddos_packets:
            # для каждой машины бота создаём свой список пакетов
            ddos_packets[source_ip] = []

        # построение пакета
        packet_list = IP(dst=dest_ip, src=source_ip) / transport_protocol / data

        current_packets = []
        for packet in packet_list:
            current_packets += [copy.deepcopy(packet) for i in range(math.floor(packets_count + 1))]

        # устанавливаем временные метки для каждого из пакетов
        for packet in current_packets:
            if protocol == 6:
                packet[TCP].flags = ''
            packet.time = current_timestamp + time_duration
            time_duration += 1

        if protocol == 6:
            packet = random.choice(current_packets)
            if packet.proto == 6:
                packet[TCP].flags = flags

        ddos_packets[source_ip] += current_packets

    current_timestamp += time_duration

if not os.path.exists('attack_data'):
    os.mkdir('attack_data')

if not os.path.exists(os.path.join('attack_data', dest_ip)):
    os.mkdir(os.path.join('attack_data', dest_ip))

# в папке с данными жертвы создаем файлы .pcap со сгенерированными сетевыми пакетами. каждый файл
# содержит в названии ip-адрес машины-бота и дату/время записи файла
for ip, packets in ddos_packets.items():
    pcap_filename = f"{ip}_{datetime.today().strftime('%d.%m.%Y_%H-%M-%S')}.pcap"
    wrpcap(os.path.join('attack_data', dest_ip, pcap_filename), packets)

# Шаг 6

print('Собираем тестовый датасет...')

dir_name = os.path.join("attack_data", dest_ip)
dir_items = os.listdir(dir_name)

# список в котором будем хранить данные полученные по каждому потоку. Потоком (flow) в этом случае будем
# считать набор пакетов, которые шли от одного комьютера-бота к атакуемой машине и обратно в рамках
# одной сессии (т.к. в течение непрерывного интервала времени)
flow_data_list = []

for item in dir_items:
    item_path = os.path.join(dir_name, item)

    # если вдруг найденный в папкет пакет не является файлом или имеет не то расширение - пропускаем его
    if not os.path.isfile(item_path) or item_path[-5:] != '.pcap':
        continue

    packet_list = rdpcap(item_path)
    flow_data = {'Flow ID': "{src_ip}-{dst_ip}-{src_port}-{dst_port}-{protocol}".format(src_ip=packet_list[0].src,
                                                                                        dst_ip=packet_list[0].dst,
                                                                                        src_port=packet_list[0].sport,
                                                                                        dst_port=packet_list[0].dport,
                                                                                        protocol=packet_list[0].proto),
                 'Src IP': packet_list[0].src, 'Src Port': packet_list[0].sport, 'Dst IP': packet_list[0].dst,
                 'Dst Port': packet_list[0].dport, 'Protocol': packet_list[0].proto}

    # Данные потока - это фактически значения полей нашего изначального датасета. В каждом файле
    # .pcap у нас хранятся данные одного потока. Соответственно используем их для формирования
    # значений тестового датасета - пока записываем их в словарь. Общие для всех пакетов данные берем
    # из первого пакета нашего потока

    # Идентификатор потока получаем используя форматирование строки

    packet_datetime = datetime.fromtimestamp(packet_list[0].time)

    flow_data['Timestamp'] = packet_datetime.strftime("%d/%m/%Y %I:%M:%S %p")

    packet_list = sorted(packet_list, key=lambda packet: packet.time)
    flow_data['Flow Duration'] = packet_list[-1].time - packet_list[0].time

    tot_fwd_pkts = len(packet_list)
    flow_data['Tot Fwd Pkts'] = tot_fwd_pkts

    fwd_iat_time = 0
    totlen_fwd_pkts = 0

    # для подсчета количества флаков в пакетах атаки используем словарь с буквенными обозначениями флагов
    flags = {}
    flags['P'] = 0
    flags['U'] = 0
    flags['S'] = 0
    flags['R'] = 0
    flags['A'] = 0
    flags['E'] = 0
    flags['C'] = 0
    flags['F'] = 0

    idle_mean = 0
    times_between_packets = []

    prev_packet = packet_list[0]

    for packet in packet_list:
        totlen_fwd_pkts += len(packet)
        fwd_iat_time += packet.time - prev_packet.time
        times_between_packets.append(packet.time - prev_packet.time)
        # считаем количество флагов в пакетах отправленных протоколу TCP
        if packet.proto == 6:
            for flag in list(packet[TCP].flags.flagrepr()):
                flags[flag] += 1

        prev_packet = packet

    # убираем лишний ноль из списка времени между пакетами
    times_between_packets.pop(0)
    times_between_packets.sort()

    # найдём в списке времени между пакетами среднее значение. всё что выше
    # этого значения будем считать активной частью потока. Всё, что выше - простоем
    # в потоке. Это простейший метод, можно поробовать более сложный метод определения
    # что является временем активного потока, а что простоя

    mean_times_between_packets = 0 if len(times_between_packets) == 0 else sum(times_between_packets) / len(
        times_between_packets)

    active_times = list(filter(lambda time: time <= mean_times_between_packets, times_between_packets))
    idle_times = list(filter(lambda time: time > mean_times_between_packets, times_between_packets))

    flow_data['TotLen Fwd Pkts'] = totlen_fwd_pkts
    flow_data['Fwd IAT Mean'] = fwd_iat_time / tot_fwd_pkts
    flow_data['Pkt Len Mean'] = totlen_fwd_pkts / tot_fwd_pkts
    flow_data['Fwd PSH Flags'] = flags['P']
    flow_data['Fwd URG Flags'] = flags['U']
    flow_data['FIN Flag Count'] = flags['F']
    flow_data['SYN Flag Cnt'] = flags['S']
    flow_data['URG Flag Cnt'] = flags['U']

    flow_data['Idle Mean'] = 0 if len(active_times) == 0 else np.mean(active_times) #sum(active_times) / len(active_times)

    flow_data['Active Mean'] = 0 if len(idle_times) == 0 else np.mean(idle_times) #sum(idle_times) / len(idle_times)
    flow_data['Idle Std'] = 0 if len(active_times) == 0 else np.std(active_times)
    # Эти данные заполняются для пакетов обратного направления
    # flow_data['Tot Bwd Pkts'] =
    # flow_data['TotLen Bwd Pkts'] =
    # flow_data['Bwd IAT Mean'] =
    # flow_data['Bwd PSH Flags'] =
    # flow_data['Bwd URG Flags'] =



    # добавляем полученный словарь данных одного потока в общий список данных о потоках:

    flow_data_list.append(flow_data)

# Шаг 7
filename = os.path.join(dir_name, f'generated_result_{datetime.now().strftime("%d.%m.%Y_%H-%M-%S")}.scv')
csv_file = open(filename, 'w', newline='')

field_names = flow_data_list[0].keys()
writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=field_names)

# записываем заголовок
writer.writeheader()

# записываем данные в таблицу
writer.writerows(flow_data_list)

# обязательно закрываем файл, для того чтобы данные из оперативной памяти были записаны на диск
csv_file.close()

print('Генерация тестового датасета закончена. Результат в файле: ' + filename)

# Файл со сгенерированным датасетом будет храниться в папке 
# attack_data/адрес_компьютера_жертвы/generated_result_дата_и_время_генерации.csv
