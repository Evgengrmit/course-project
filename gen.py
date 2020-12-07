"""
Это файл интерфейса программа
Его единственная проблема - интерфейс блокируется, если нажать на какую-то из кнопок.
Пока не нашёл как решить это вопрос
"""
import sys, os, time

from tkinter import *
from threading import Thread

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from generator.ddos_generator import DdosGenerator, ThreadState


class GuiApp:

    def __init__(self):
        self.thread_state = ThreadState()
        self.ddos_generator = DdosGenerator()

        self.window = Tk()

        self.window.geometry('500x200')
        self.window.title('Генератор DDOS-атаки')

        frame1 = Frame(self.window)
        frame1.pack(fill=X)

        dest_ip_lb = Label(frame1, text="IP-адрес жертвы", justify=RIGHT, width=30)
        dest_ip_lb.pack(side=LEFT, padx=5, pady=5)

        dest_ip_edit = Entry(frame1)
        dest_ip_edit.pack(fill=X, padx=5, expand=True)

        frame2 = Frame(self.window)
        frame2.pack(fill=X)

        dest_port_lb = Label(frame2, text="Сетевой порт жертвы (80 или 443)", justify=RIGHT, width=30)
        dest_port_lb.pack(side=LEFT, padx=5, pady=5)

        dest_port_edit = Entry(frame2)
        dest_port_edit.pack(fill=X, padx=5, expand=True)

        frame3 = Frame(self.window)
        frame3.pack(fill=X)

        bots_count_lb = Label(frame3, text="Количество ботов (от 1 до 34)", justify=RIGHT, width=30)
        bots_count_lb.pack(side=LEFT, padx=5, pady=5)

        bots_count_edit = Entry(frame3)
        bots_count_edit.pack(fill=X, padx=5, expand=True)

        frame4 = Frame(self.window)
        frame4.pack(fill=X)

        frame5 = Frame(self.window)

        self.process_lb = Label(frame5, text="Введите параметры ddos атаки", justify=CENTER, width=90,
                                fg="#875642", font="Arial 11")
        self.process_lb.pack(padx=5, pady=5)

        self.generate_packets_btn = Button(frame4, text="Сгенерировать сетевые пакеты", width=35,
                                           command=lambda: self.generate_packets(self.ddos_generator,
                                                                                 dest_ip_edit.get(),
                                                                                 dest_port_edit.get(),
                                                                                 bots_count_edit.get()))
        self.generate_packets_btn.pack(side=LEFT, padx=5, pady=5)

        self.make_dataset_btn = Button(frame4, text="Собрать итоговый датасет", width=35,
                                       command=lambda: self.make_dataset(self.ddos_generator, dest_ip_edit.get()))
        self.make_dataset_btn.pack(side=RIGHT, padx=5, pady=5)

        frame5.pack(fill=X)

    def generate_packets(self, ddos_generator, dest_ip, dest_port, bots_count):
        self.process_lb['text'] = "Выполняется процесс генерации сетевых пакетов...Ожидайте"

        self.generate_packets_btn.config(state=DISABLED)
        self.make_dataset_btn.config(state=DISABLED)

        packets_generate_th = Thread(target=ddos_generator.generate_packets,
                                     args=(dest_ip, int(dest_port), int(bots_count), self.thread_state))
        # self.window.after(100, lambda: packets_generate_th.start())
        packets_generate_th.start()
        packets_generate_th.join()
        # self.window.after(10000, packets_generate_th.join())

        self.generate_packets_btn.config(state=NORMAL)
        self.make_dataset_btn.config(state=NORMAL)

        # ddos_generator.generate_packets()

        self.process_lb['text'] = "Сетевые пакеты сгенерированы. Можете собрать тестовый датасет!"

    def make_dataset(self, ddos_generator, dest_ip):
        self.process_lb['text'] = "Выполняется процесс сборки тестового датасета...Ожидайте"

        self.generate_packets_btn.config(state=DISABLED)
        self.make_dataset_btn.config(state=DISABLED)

        dataset_making_th = Thread(target=ddos_generator.make_test_dataset, args=(dest_ip, self.thread_state))
        # self.window.after(200, lambda: dataset_making_th.start())
        dataset_making_th.start()
        dataset_making_th.join()
        # self.window.after(5000,dataset_making_th.join())

        self.generate_packets_btn.config(state=NORMAL)
        self.make_dataset_btn.config(state=NORMAL)

        self.process_lb['text'] = "Процедура формирования тестового датасета завершена!"

    def __del__(self):
        self.thread_state.stop = True
        self.window.destroy()

    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.__del__)

        self.window.mainloop()


if __name__ == '__main__':
    app = GuiApp()
    app.run()
