import pika
import numpy as np
from sklearn.datasets import load_diabetes
import json
import time
from datetime import datetime

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)

# Создаём подключение к серверу на локальном хосте:
# connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
# Создаём подключение к rabbitmq в докере
connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

# Создаём очередь y_true
channel.queue_declare(queue="y_true")
# Создаём очередь features
channel.queue_declare(queue="features")
# Создаём очередь notification, для того, чтобы сервис plot знал об очередной итерации отправки данных
channel.queue_declare(queue="notification")

# бесконечный цикл отправки сообщений
while True:
    # Формируем случайный индекс строки
    random_row = np.random.randint(0, X.shape[0] - 1)
    message_id = datetime.timestamp(datetime.now())

    # формируем словари с сообщениями, в которые добавляем id сообщения
    message_y_true = {"id": message_id, "body": y[random_row]}
    message_features = {"id": message_id, "body": list(X[random_row])}

    # Публикуем сообщение в очередь features
    channel.basic_publish(
        exchange="", routing_key="features", body=json.dumps(message_features)
    )
    # print('Сообщение с вектором признаков отправлено в очередь')

    # добавляем задержку между отправкой фич и истинного значения в очереди
    time.sleep(0.5)

    # Публикуем сообщение в очередь y_true
    channel.basic_publish(
        exchange="", routing_key="y_true", body=json.dumps(message_y_true)
    )
    # print('Сообщение с правильным ответом отправлено в очередь')

    channel.basic_publish(
        exchange="", routing_key="notification", body=json.dumps(True)
    )
    print("features, y_true и нотификация отправлены в очереди...")

    # добавляем еще одну задержку
    time.sleep(1)
