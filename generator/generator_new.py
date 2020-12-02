import csv

import random
import datetime
from scapy.all import *

file = open("ddos_src.csv", "r")

csv_reader = csv.DictReader(file, delimiter=",")

ddos_data = []

for data in csv_reader:
    ddos_data.append(data)
ports = ddos_data[0]['Src Port'].split(" ")
# print(len(ports))

file.close()

# Шаг 2. Выбираем бота (комьпютер-источник атаки)

source = random.choice(ddos_data)

source_ip = source['Src IP']
# выбираем случайным образом порт для атаки (исходящий порт)
source_port = int(random.choice(source['Src Port'].split(' ')))
protocol = int(random.choice(source['Protocol'].split(' ')))
packets_count = int(float(source['Tot Fwd Pkts']))

# Шаг 3. Выбираем комьпютер жертву
dest_ip = random.choice(source['Dst IP'].split(' '))
dest_port = int(random.choice(source['Dst Port'].split(' ')))

dest_ip = input("Введите ip-адрес жертвы: ")

# Атакуемые порты
dest_ports = map(int, input("Укажите через пробел атакуемые порты (80/443):").split(' '))

attack_time = int(input("Укажите время атаки в секундах: "))

# число машин для атаки 
bots_count = random.randint(5, len(ddos_data))

ddos_packets = {}
# Пока последовательно позже параллельно

start_timestamp = datetime.now().timestamp()

current_timestamp = start_timestamp

while current_timestamp < start_timestamp + attack_time:

    for i in range(bots_count):
        time_duration = 1
        source = random.choice(ddos_data)
        source_ip = source['Src IP']
        source_port = int(random.choice(source['Src Port'].split(' ')))
        protocol = int(random.choice(source['Protocol'].split(' ')))
        packets_count = int(float(source['Tot Fwd Pkts']))

        flags = []

        data = random._urandom(1024)

        if source_port == 6:
            transport_protocol = TCP(sport=source_port, dport=dest_ports)

            if source['SYN Flag Cnt']:
                flags.append('S')

            if source['ACK Flag Cnt']:
                flags.append('A')

            if source['RST Flag Cnt']:
                flags.append('R')

            if source['URG Flag Cnt']:
                flags.append('U')

            if source['FIN Flag Cnt']:
                flags.append('F')

            if source['CWE Flag Cnt']:
                flags.append('E')

            if source['CWE Flag Cnt']:
                flags.append('P')
        else:
            transport_protocol = UDP(dport=int(source_port))

        if source_ip not in ddos_packets:
            ddos_packets[source_ip] = []

        packet = IP(dst=dest_ip) / transport_protocol / data

        current_packets = [packet] * packets_count

        if source_port == 6:
            for flag in flags:
                packet = random.choice(current_packets)
                packet[TCP].flags += flag

        for packet in current_packets:
            packet.time = current_timestamp + time_duration
            time_duration += 1

        ddos_packets[source_ip] += current_packets

    current_timestamp += time_duration


if not os.path.exists('attack_data'):
    os.mkdir('attack_data')

if not os.path.exists(os.path.join('attack_data', dest_ip)):
    os.mkdir(os.path.join('attack_data', dest_ip))

for ip, packets in ddos_packets.items():
    pcap_filename = f"{ip}_{datetime.today().strftime('%d.%m.%Y_%H-%M-%S')}.pcap"
    wrpcap(os.path.join('attack_data', dest_ip, pcap_filename), packets)
