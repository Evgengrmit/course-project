import unittest
import datetime, os, random, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../course-project"))

from generator.ddos_generator import DdosGenerator
from scapy.layers.inet import IP, TCP
'''import sys
sys.path.append("..")'''


class TestGenerator(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestGenerator, self).__init__(*args, **kwargs)
        self.generator = DdosGenerator()

    def setUp(self):

        self.packet_length = 56
        self.packet_timestamp = datetime.datetime.now().timestamp()

        self.dest_ip = ''
        self.source_ip = ''

        for i in range(0, 4):
            self.dest_ip += str(random.randint(0, 255)) + '.'
            self.source_ip += str(random.randint(0, 255)) + '.'

        self.dest_ip = self.dest_ip[:-1]
        self.source_ip = self.source_ip[:-1]

        self.all_packets_count = random.randint(10, 20)
        self.syn_flag_count = 1
        self.urg_flag_count = 1
        self.fin_flag_count = 1
        self.psh_flag_count = 1

        self.source_port = random.randint(1, 65535)
        self.protocol = 6
        self.dest_port = 443

        self.delay_between_packets = random.randint(5, 40)
        self.packets_count = random.randint(1, 10)
        self.packet_len_avg = random.randint(40, 100)
        self.packet_len_std = random.randint(15, 35)

    def test_load_prepered_datatset(self):
        self.assertNotEqual(len(self.generator._ddos_data), 0)

    def _test_packet(self, packet):

        self.assertIsInstance(packet, IP)

        self.assertIn('S', packet[TCP].flags.flagrepr())
        self.assertIn('U', packet[TCP].flags.flagrepr())
        self.assertIn('F', packet[TCP].flags.flagrepr())
        self.assertIn('P', packet[TCP].flags.flagrepr())

        self.assertEqual(packet.src, self.source_ip)
        self.assertEqual(packet.dst, self.dest_ip)

        self.assertEqual(packet.sport, self.source_port)
        self.assertEqual(packet.dport, self.dest_port)

        self.assertEqual(packet.proto, self.protocol)

    def test_creating_packet(self):

        packet = self.generator._create_packet(self.packet_length, self.packet_timestamp, self.all_packets_count,
                                               self.syn_flag_count, self.urg_flag_count, self.fin_flag_count,
                                               self.psh_flag_count, self.source_ip,
                                               self.source_port, self.protocol, self.dest_ip, self.dest_port)

        self.assertIsInstance(packet, IP)

        self.assertEqual(len(packet), self.packet_length)
        self.assertEqual(len(packet.load), self.packet_length - 40)

        self.assertEqual(int(packet.time), int(self.packet_timestamp))

        self._test_packet(packet)

    def test_creating_packets_set(self):
        packets_list = self.generator._create_packet_set(self.packets_count, self.packet_len_avg, self.packet_len_std,
                                                         self.packet_timestamp, self.all_packets_count,
                                                         self.syn_flag_count, self.urg_flag_count, self.fin_flag_count,
                                                         self.psh_flag_count, self.source_ip, self.source_port,
                                                         self.protocol, self.dest_ip, self.dest_port,
                                                         self.delay_between_packets)

        self.assertEqual(len(packets_list), self.packets_count)

        for packet in packets_list:
            self._test_packet(packet)

    def test_saving_packets(self):

        packets_list = self.generator._create_packet_set(self.packets_count, self.packet_len_avg, self.packet_len_std,
                                                         self.packet_timestamp, self.all_packets_count,
                                                         self.syn_flag_count, self.urg_flag_count, self.fin_flag_count,
                                                         self.psh_flag_count, self.source_ip, self.source_port,
                                                         self.protocol, self.dest_ip, self.dest_port,
                                                         self.delay_between_packets)

        self.generator._save_packets(packets_list, self.source_ip, self.dest_ip)

        self.assertTrue(os.path.exists(self.generator._result_dir))
        
        dir_name = os.path.join(self.generator._result_dir, self.dest_ip)

        self.assertTrue(os.path.exists(dir_name))

        dir_items = os.listdir(dir_name)

        self.assertEqual(len(dir_items), 1)

        item_path = os.path.join(dir_name, dir_items[0])
        self.assertTrue(os.path.isfile(item_path))

        self.assertIn('.pcap', dir_items[0])
        self.assertIn(f"{self.source_ip}_{datetime.datetime.today().strftime('%d.%m.%Y')}", dir_items[0])


if __name__ == '__main__':
    unittest.main()