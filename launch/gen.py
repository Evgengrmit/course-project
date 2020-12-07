import sys

sys.path.append("..")
from generator import generator
from tkinter import *
import time


def generate_packets(ddos_generator, process_label, dest_ip, dest_port, bots_count):
    process_label['text'] = "Выполняется процесс генерации сетевых пакетов...Ожидайте"
    time.sleep(2)

    ddos_generator.generate_packets(dest_ip, int(dest_port), int(bots_count))

    process_label['text'] = "Сетевые пакеты сгенерированы. Можете собрать тестовый датасет!"


def make_dataset(ddos_generator, process_label, dest_ip):
    process_label['text'] = "Выполняется процесс сборки тестового датасета...Ожидайте"
    time.sleep(2)

    dataset_filename_path = ddos_generator.make_test_dataset(dest_ip)

    process_label['text'] = "Результат: " + dataset_filename_path


def main():
    # создаем окно приложения. задаем его размеры и название программы в заголовке
    window = Tk()
    window.geometry('500x200')
    window.title('Генератор DDOS-атаки')

    ddos_generator = generator.DdosGenerator()

    frame1 = Frame(window)
    frame1.pack(fill=X)

    dest_ip_lb = Label(frame1, text="IP-адрес жертвы", justify=RIGHT, width=30)
    dest_ip_lb.pack(side=LEFT, padx=5, pady=5)

    dest_ip_edit = Entry(frame1)
    dest_ip_edit.pack(fill=X, padx=5, expand=True)

    frame2 = Frame(window)
    frame2.pack(fill=X)

    dest_port_lb = Label(frame2, text="Сетевой порт жертвы (80 или 443)", justify=RIGHT, width=30)
    dest_port_lb.pack(side=LEFT, padx=5, pady=5)

    dest_port_edit = Entry(frame2)
    dest_port_edit.pack(fill=X, padx=5, expand=True)

    frame3 = Frame(window)
    frame3.pack(fill=X)

    bots_count_lb = Label(frame3, text="Количество ботов (от 1 до 34)", justify=RIGHT, width=30)
    bots_count_lb.pack(side=LEFT, padx=5, pady=5)

    bots_count_edit = Entry(frame3)
    bots_count_edit.pack(fill=X, padx=5, expand=True)

    frame4 = Frame(window)
    frame4.pack(fill=X)

    frame5 = Frame(window)

    process_lb = Label(frame5, text="Введите параметры ddos атаки", justify=CENTER, width=90,
                       fg="#875642", font="Arial 11")
    process_lb.pack(padx=5, pady=5)

    generate_packets_btn = Button(frame4, text="Сгенерировать сетевые пакеты", width=35,
                                  command=lambda: generate_packets(ddos_generator, process_lb, dest_ip_edit.get(),
                                                                   dest_port_edit.get(), bots_count_edit.get()))
    generate_packets_btn.pack(side=LEFT, padx=5, pady=5)

    make_dataset_btn = Button(frame4, text="Собрать итоговый датасет", width=35,
                              command=lambda: make_dataset(ddos_generator, process_lb, dest_ip_edit.get()))
    make_dataset_btn.pack(side=RIGHT, padx=5, pady=5)

    frame5.pack(fill=X)

    window.mainloop()


if __name__ == '__main__':
    main()
