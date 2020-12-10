import csv
import datetime

from scapy.all import *

script_path = os.path.dirname(os.path.abspath(__file__))


# класс состояния потоков. Методы генерации пакетов и формирования тестового датасета запускаются
# в потоках.
class ThreadState:

    def __init__(self):
        self.stop = False


class DdosGenerator:

    def __init__(self):

        print('Загружаем данные базового датасета...')

        self._result_dir = os.path.join(script_path, 'attack_data')

        prepared_dataset_path = os.path.join(script_path, 'ddos_benign_src.csv')

        with open(prepared_dataset_path, "r") as file:
            csv_reader = csv.DictReader(file, delimiter=",")

            self._ddos_data = []

            for data in csv_reader:
                self._ddos_data.append(data)

    def _create_packet(self, packet_length, packet_timestamp, all_packets_count, syn_flag_count,
                       urg_flag_count, fin_flag_count, psh_flag_count, source_ip, source_port, protocol, dest_ip,
                       dest_port):

        """
           Генерация одного сетевого пакета
        """
        if protocol == 6:

            flags = ''

            if random.uniform(0, all_packets_count) <= syn_flag_count * all_packets_count:
                flags += 'S'

            if random.uniform(0, all_packets_count) <= urg_flag_count * all_packets_count:
                flags += 'U'

            if random.uniform(0, all_packets_count) <= fin_flag_count * all_packets_count:
                flags += 'F'

            if random.uniform(0, all_packets_count) <= psh_flag_count * all_packets_count:
                flags += 'P'

            transport_protocol = TCP(sport=source_port, dport=dest_port)
            transport_protocol.flags = flags
        else:
            transport_protocol = UDP(dport=dest_port)

        net_protocol = IP(dst=dest_ip, src=source_ip)

        data_length = int(packet_length - len(net_protocol) - len(transport_protocol))

        if data_length < 0:
            data_length = 0

        packet_data = os.urandom(data_length)

        packet_list = net_protocol / transport_protocol / packet_data

        for packet in packet_list:
            packet.time = packet_timestamp

        return packet_list

    def _save_packets(self, packets_list, source_ip, dest_ip):
        """
           сохранение пакетов одного потока (flow) одной атакующей
           машины в .pcap файл
        """
        if len(packets_list) == 0:
            return

        if not os.path.exists(self._result_dir):
            os.mkdir(self._result_dir)

        if not os.path.exists(os.path.join(self._result_dir, dest_ip)):
            os.mkdir(os.path.join(self._result_dir, dest_ip))

        pcap_filename = f"{source_ip}_{datetime.today().strftime('%d.%m.%Y_%H-%M-%S.%f')}.pcap"
        wrpcap(os.path.join(self._result_dir, dest_ip, pcap_filename), packets_list)

    def _create_packet_list(self, packets_count, packet_len_avg, packet_len_std, current_timestamp,
                            all_packets_count, syn_flag_count, urg_flag_count, fin_flag_count, psh_fwd_flag_count,
                            source_ip,
                            source_port, protocol, dest_ip, dest_port, delay_between_packets, thread_state):
        """
           Создает набор пакетов по заданным параметрам
        """
        packet_list = []

        for packet_number in range(packets_count):

            if thread_state.stop:
                return

            # выбираем по закону нормального распределения длину пакета на основе данных предварительного датасета
            packet_len = random.normalvariate(packet_len_avg, packet_len_std)
            while packet_len < 0:
                packet_len = random.normalvariate(packet_len_avg, packet_len_std)

            packet = self._create_packet(packet_len, current_timestamp, all_packets_count, syn_flag_count,
                                         urg_flag_count, fin_flag_count, psh_fwd_flag_count, source_ip, source_port,
                                         protocol,
                                         dest_ip, dest_port)

            packet_list += packet

            # смещаем время отправки для следующего пакета на величину времени между пакетами
            current_timestamp += delay_between_packets

        return packet_list

    def _generate_flows(self, flow_counts, source, current_timestamp, start_timestamp, source_ip, source_port,
                        protocol, dest_ip, dest_port, thread_state):

        for flow_number in range(flow_counts):

            if thread_state.stop:
                return

            print(f'Генерируем поток пакетов {flow_number + 1} (всего {flow_counts})...', end='\r')

            # выбираем по закону нормального распределения продолжительность потока
            flow_duration = random.normalvariate(float(source['Flow Duration Mean']),
                                                 float(source['Flow Duration Std']))
            while flow_duration <= 0:
                flow_duration = random.normalvariate(float(source['Flow Duration Mean']),
                                                     float(source['Flow Duration Std']))

            # микросекунды -> секунды
            flow_duration /= 10 ** 6

            # соотношение средней продолжительности потока для данной машины и выбранного значения.
            packets_count_ratio = flow_duration / (float(source['Flow Duration Mean']) / 10 ** 6)

            packets_fwd_count = int(float(source['Tot Fwd Pkts']) * packets_count_ratio)
            packets_bwd_count = int(float(source['Tot Bwd Pkts']) * packets_count_ratio)

            all_packets_count = packets_fwd_count + packets_bwd_count

            syn_flag_count = float(source['SYN Flag Cnt'])
            urg_flag_count = float(source['URG Flag Cnt'])
            fin_flag_count = float(source['FIN Flag Cnt'])

            psh_fwd_flag_count = float(source['Fwd PSH Flags'])

            packet_list = []

            if packets_fwd_count > 0:
                # вычисляем задержку между отправляемыми пакетами.
                delay_between_fwd_packets = flow_duration / packets_fwd_count

                packet_list += self._create_packet_list(packets_fwd_count, float(source['Fwd Pkt Len Mean']),
                                                        float(source['Fwd Pkt Len Std']), current_timestamp,
                                                        all_packets_count, syn_flag_count, urg_flag_count,
                                                        fin_flag_count, psh_fwd_flag_count, source_ip, source_port,
                                                        protocol, dest_ip, dest_port, delay_between_fwd_packets,
                                                        thread_state)

            # psh_bwd_flag_count = float(source['Bwd PSH Flags'])

            # вычисляем задержку для пакетов, отправляемых в обратную сторону и время отправки первого пакета
            # delay_between_bwd_packets = 0

            if packets_bwd_count > 0:
                delay_between_bwd_packets = flow_duration / packets_bwd_count
                current_timestamp = start_timestamp + delay_between_bwd_packets

                packet_list += self._create_packet_list(packets_bwd_count, float(source['Bwd Pkt Len Mean']),
                                                        float(source['Bwd Pkt Len Std']), current_timestamp,
                                                        all_packets_count, syn_flag_count, urg_flag_count,
                                                        fin_flag_count, psh_fwd_flag_count, source_ip, source_port,
                                                        protocol, dest_ip, dest_port, delay_between_bwd_packets,
                                                        thread_state)

            # вычисляем время между потоками и сдвигаем время отправки первого пакета из следующего потока
            # на эту величину
            delay_between_flows = random.normalvariate(float(source['Flow IAT Mean']),
                                                       float(source['Flow IAT Std']))

            current_timestamp = start_timestamp + flow_duration + delay_between_flows / 10 ** 6

            self._save_packets(packet_list, source_ip, dest_ip)

    def generate_packets(self, dest_ip, dest_port, bots_count, thread_state):
        """
           Генерация пакетов для всех машин ботов
        """
        # ddos_packets = {}
        start_timestamp = datetime.now().timestamp()

        print(f'Всего ботов {bots_count}')
        print('Генерируем сетевые пакеты...')

        for bot_number in range(bots_count):
            print(f'Для бота {bot_number}...')

            # фиксируем время начала атаки. Для всех машин оно будет одинаковое
            current_timestamp = start_timestamp

            # получаем исходные данные одной из атакующих машин
            source = random.choice(self._ddos_data)
            source_ip = source['Src IP']
            source_port = int(random.choice(source['Src Port'].split(' ')))
            protocol = int(random.choice(source['Protocol'].split(' ')))

            # вычисляем число потоков атаки. Выбираем случайное значение по закону нормального распределения
            # исходя из среднего количества потоков для данного бота в предварительном датасете, и его
            # среднеквадратического отклонения
            flow_counts = math.ceil(
                random.normalvariate(float(source['Flows Cnt Mean']), float(source['Flows Cnt Std'])))
            while flow_counts < 0:
                flow_counts = math.ceil(
                    random.normalvariate(float(source['Flows Cnt Mean']), float(source['Flows Cnt Std'])))

            self._generate_flows(flow_counts, source, current_timestamp, start_timestamp, source_ip, source_port,
                                 protocol, dest_ip, dest_port, thread_state)

            print()

        print("Формирование сетевых пакетов завершено")

    def make_test_dataset(self, dest_ip, thread_state):
        """
          Вычисление данных о сгенерированных сетевых пакетах и сборки итогового тестового датасета
        """
        print('Собираем тестовый датасет...')

        dir_name = os.path.join(self._result_dir, dest_ip)
        dir_items = os.listdir(dir_name)

        src_data = {}

        for item in dir_items:
            item_path = os.path.join(dir_name, item)

            if not os.path.isfile(item_path) or item_path[-5:] != '.pcap':
                continue

            packet_list = rdpcap(item_path)
            flow_data = {}

            sourse_ip = packet_list[0].src

            # src_data - словарь, где ключом будет ip-адрес бота, а значением - список потоков пакетов от этого бота
            # к жертве и обратно
            if sourse_ip not in src_data:
                src_data[sourse_ip] = []

            flow_data['Flow ID'] = "{src_ip}-{dst_ip}-{src_port}-{dst_port}-{protocol}".format(src_ip=sourse_ip,
                                                                                               dst_ip=packet_list[
                                                                                                   0].dst,
                                                                                               src_port=packet_list[
                                                                                                   0].sport,
                                                                                               dst_port=packet_list[
                                                                                                   0].dport,
                                                                                               protocol=packet_list[
                                                                                                   0].proto)

            flow_data['Src IP'] = packet_list[0].src
            flow_data['Src Port'] = packet_list[0].sport
            flow_data['Dst IP'] = packet_list[0].dst
            flow_data['Dst Port'] = packet_list[0].dport
            flow_data['Protocol'] = packet_list[0].proto

            packet_datetime = datetime.fromtimestamp(packet_list[0].time)
            flow_data['Timestamp'] = packet_datetime.strftime("%d/%m/%Y %I:%M:%S %p")

            #  время начала и конца потока для вычисления интервала между потоками, простоев и активных фаз потоков
            flow_data['Flow Start Timestamp'] = packet_list[0].time
            flow_data['Flow End Timestamp'] = packet_list[-1].time

            packet_list = sorted(packet_list, key=lambda packet: packet.time)
            # sec to microsec
            flow_duration_seconds = packet_list[-1].time - packet_list[0].time
            flow_data['Flow Duration'] = flow_duration_seconds * 10 ** 6

            flags = {'S': 0, 'U': 0, 'F': 0, 'fwd_P': 0, 'bwd_P': 0}

            fwd_pkts_total_cnt = 0
            bwd_pkts_total_cnt = 0

            bwd_pkts_len_max = 0

            # среднеквадратическое отклонение времени простоя потока
            # idle_std = 0

            flow_total_bytes = 0

            fwd_total_bytes = 0
            bwd_total_bytes = 0

            for packet in packet_list:

                if thread_state.stop:
                    return

                flow_total_bytes += len(packet)

                try:
                    if bwd_pkts_len_max < len(packet.load):
                        bwd_pkts_len_max = len(packet.load)
                except AttributeError:
                    pass

                if packet.src != dest_ip:
                    fwd_pkts_total_cnt += 1
                    fwd_total_bytes += len(packet)
                else:
                    bwd_pkts_total_cnt += 1
                    bwd_total_bytes += len(packet)

                if packet.proto == 6:
                    for flag in list(packet[TCP].flags.flagrepr()):
                        if flag != 'P':
                            flags[flag] += 1
                        else:
                            if packet.src != dest_ip:
                                flags['fwd_P'] += 1
                            else:
                                flags['bwd_P'] += 1

            flow_data['Tot Fwd Pkts'] = fwd_pkts_total_cnt
            flow_data['Tot Bwd Pkts'] = bwd_pkts_total_cnt

            flow_data['SYN Flag Cnt'] = flags['S']
            flow_data['URG Flag Cnt'] = flags['U']
            flow_data['FIN Flag Cnt'] = flags['F']

            flow_data['Fwd PSH Flags'] = flags['fwd_P']
            flow_data['Bwd PSH Flags'] = flags['bwd_P']

            flow_data['Bwd Pkt Len Max'] = bwd_pkts_len_max
            flow_data['Bwd Pkts/s'] = 0 if flow_duration_seconds == 0 else bwd_pkts_total_cnt / flow_duration_seconds

            flow_data['Flow Byts/s'] = 0 if flow_duration_seconds == 0 else flow_total_bytes / flow_duration_seconds
            flow_data['Flow Pkts/s'] = 0 if flow_duration_seconds == 0 else len(packet_list) / flow_duration_seconds

            flow_data['Down/Up Ratio'] = 0 if fwd_total_bytes == 0 else bwd_total_bytes / fwd_total_bytes

            # Для заполнения заголовка файла. Ниже вычисляем их значения и заполняем итоговый словарь
            flow_data['Flow IAT Mean'] = 0
            flow_data['Active Mean'] = 0
            flow_data['Idle Std'] = 0

            src_data[sourse_ip].append(flow_data)

        filename = os.path.join(dir_name, f'../generated_result_{datetime.now().strftime("%d.%m.%Y_%H-%M-%S")}.csv')
        csv_file = open(filename, 'w', newline='')

        field_names = list(list(src_data.values())[0][0].keys())
        writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=field_names)

        writer.writeheader()

        # время между потоками, активность и простои потоков
        for src, flow_list in src_data.items():

            if thread_state.stop:
                return

            flow_list = sorted(flow_list, key=lambda flow_data: flow_data['Flow Start Timestamp'])

            avg_time_between_flows = 0
            avg_flow_active = flow_list[0]['Flow Duration']
            flow_idles = []

            prev_flow = flow_list[0]

            for flow_num in range(1, len(flow_list)):
                avg_time_between_flows += (flow_list[flow_num]['Flow Start Timestamp'] - prev_flow[
                    'Flow End Timestamp']) * 10 ** 6
                flow_idles.append(
                    (flow_list[flow_num]['Flow Start Timestamp'] - prev_flow['Flow End Timestamp']) * 10 ** 6)
                avg_flow_active += flow_list[flow_num]['Flow Duration']
                prev_flow = flow_list[flow_num]

            avg_time_between_flows = 0 if len(flow_idles) == 0 else avg_time_between_flows / len(flow_idles)
            avg_flow_active = 0 if len(flow_list) == 0 else avg_flow_active / len(flow_list)

            std_flow_idles = 0

            for idle in flow_idles:
                std_flow_idles += (avg_time_between_flows - idle) ** 2

            # вычисляем среднеквадратическое отклонение времени потока
            # вычисление производилось на основании основании несмещённой оценки дисперсии
            std_flow_idles = math.sqrt(1 / (len(flow_idles) - 1) * std_flow_idles)

            for flow_data in flow_list:
                flow_data['Flow IAT Mean'] = avg_time_between_flows
                flow_data['Active Mean'] = avg_flow_active
                flow_data['Idle Std'] = std_flow_idles

            writer.writerows(flow_list)

        csv_file.close()

        print("Сборка тестового датасета завершена")

        return filename
