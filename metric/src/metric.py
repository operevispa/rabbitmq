import pika
import json
import csv
import os


def callback(ch, method, properties, body):
    """Создаём функцию callback для обработки данных из очередией"""

    # проводим десериализацию полученных данных с помощью json.loads()
    uns_message = json.loads(body)
    id = uns_message["id"]
    y = uns_message["body"]

    # поскольку мы "слушаем" более 1 очереди, нам нужно определить,
    # из какой очереди поступило сообщение и внести данные в нужный словарь
    if method.routing_key == "y_true":
        y_true_dict[id] = y
    else:
        y_pred_dict[id] = y

    # проверяем наличие пары
    if id in y_true_dict and id in y_pred_dict:
        y_true = y_true_dict.pop(id)
        y_pred = y_pred_dict.pop(id)
        abs_error = abs(y_true - y_pred)
        print(f"id={id}, abs_error={abs_error:.2f}")

        # записываем данные в файл
        csv_writer.writerow([id, y_true, y_pred, abs_error])
        csv_file.flush()


if __name__ == "__main__":
    # директория для хранения логов в докере
    logdir = f"{os.path.dirname(os.path.dirname(__file__))}/logs"
    # директория для хранения логов для локальной разработки
    # logdir = f"{os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}/logs"
    # создаем директорию logs, если она не существует
    os.makedirs(logdir, exist_ok=True)

    # Создаём подключение к серверу на локальном хосте:
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    # Создаём подключение к rabbitmq в докере
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Объявляем очередь y_true из которой будем получать истинные значения предиктора
    channel.queue_declare(queue="y_true")

    # Объявляем очередь y_pred из которой будем получать предсказания модели
    channel.queue_declare(queue="y_pred")

    # Открываем файл csv для записи данных
    csv_file = open(f"{logdir}/metric_log.csv", "w", newline="")
    csv_writer = csv.writer(csv_file)
    # записываем заголовки
    csv_writer.writerow(["id", "y_true", "y_pred", "absolute_error"])

    # определеям словари для сохранения данных
    y_true_dict = {}
    y_pred_dict = {}

    # Извлекаем сообщение из очереди y_true
    channel.basic_consume(queue="y_true", on_message_callback=callback, auto_ack=True)

    # Извлекаем сообщение из очереди y_pred
    channel.basic_consume(queue="y_pred", on_message_callback=callback, auto_ack=True)
    print("...Ожидание сообщений, для выхода нажмите CTRL+C")

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
