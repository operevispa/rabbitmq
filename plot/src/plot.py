import pika
import numpy as np
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import json

# директория хранения логов для работы в докер
LOG_DIR = f"{os.path.dirname(os.path.dirname(__file__))}/logs"
# для локального запуска
# LOG_DIR = f"{os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}/logs"
# формируем пути к файлам
LOG_FNAME = f"{LOG_DIR}/metric_log.csv"
PLOT_FNAME = f"{LOG_DIR}/error_distribution.png"


def draw_plot():
    """Функция формирует гистограмму из файла и сохраняет png файл в логи"""
    df = pd.read_csv(LOG_FNAME)
    # Проверка наличия колонки 'absolute_error'
    if "absolute_error" in df.columns:
        # Построение гистограммы распределения ошибок
        plt.figure(figsize=(10, 6))
        plt.hist(df["absolute_error"], bins=30, color="red", alpha=0.7)
        plt.title("Распределение абсолютной ошибки")
        plt.xlabel("Абсолютная ошибка")
        plt.ylabel("Частота")

        # Сохранение графика в файл
        plt.savefig(PLOT_FNAME)
        # Закрываем файл после сохранения
        plt.close()
    else:
        print("Колонка 'absolute_error' не найдена в DataFrame.")

    print("Гистограмма актуализирована...")


def callback(ch, method, properties, body):
    """Функцию callback для обработки данных из очереди notification"""
    # проводим десериализацию полученных данных с помощью json.loads()
    uns_message = json.loads(body)
    if uns_message:
        draw_plot()


if __name__ == "__main__":
    # создаем директорию logs, если она не существует
    os.makedirs(LOG_DIR, exist_ok=True)

    # Создаём подключение к серверу на локальном хосте:
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    # Создаём подключение к rabbitmq в докере
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Поскольку в задании не однозначно изложены требования в части условия формирования гистограммы
    # то реализованы два варианта: через нотификацию отельной очереди rabbitmq и по таймеру в 10 сек

    # Вариант 1
    # Извлекаем сообщение из очереди notification
    # on_message_callback показывает, какую функцию вызвать при получении сообщения
    channel.basic_consume(
        queue="notification", on_message_callback=callback, auto_ack=True
    )
    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()

    # Вариант 2 - обновление в вечном цикле через feature_cycle_time секунд (равное двум таймаутам в features.py)
    # поскольку варианты не могут работать параллельно, данный вариант закомментирован
    # feature_cycle_time = 1.5
    # while True:
    #     draw_plot()
    #     time.sleep(feature_cycle_time)
    #     print("Гистограмма актуализирована")
