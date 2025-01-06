import pika
import pickle
import numpy as np
import os
import json


def callback(ch, method, properties, body):
    """Функция callback для обработки данных из очереди y_pred"""
    # проводим десериализацию полученных данных с помощью json.loads()
    unserrialized_message = json.loads(body)
    message_id = unserrialized_message["id"]

    # приводим список к numpy-массиву размерности (1, m), где m - количесвто признаков
    features = np.array(unserrialized_message["body"]).reshape(1, -1)

    # предсказываем значение предиктора. а поскольку возвращается массив, получаем нулевое значение массива
    prediction = regressor.predict(features)[0]

    # формируем сообщение для последующей сериализации (добавляя полученный id)
    message_y_pred = {"id": message_id, "body": prediction}

    # Публикуем предсказанное значение предиктора в очередь y_pred
    # предварительно сериализуем значение переменной prediction
    channel.basic_publish(
        exchange="", routing_key="y_pred", body=json.dumps(message_y_pred)
    )

    print(f"Предсказание {prediction} отправлено в очередь y_pred")


if __name__ == "__main__":
    # получаем точный путь до файла скрипта, чтобы ну мучаться с относительными путями и местом запуска скрипта
    current_dir = os.path.dirname(__file__)

    # Читаем файл с сериализованной моделью
    with open(f"{current_dir}/myfile.pkl", "rb") as pkl_file:
        regressor = pickle.load(pkl_file)

    # Создаём подключение к серверу на локальном хосте:
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Объявляем очередь features из которой будем получать признаки
    channel.queue_declare(queue="features")

    # Объявляем очередь  y_pred в которую будем отправлять предсказания модели
    channel.queue_declare(queue="y_pred")

    # Извлекаем сообщение из очереди features
    # on_message_callback показывает, какую функцию вызвать при получении сообщения
    channel.basic_consume(queue="features", on_message_callback=callback, auto_ack=True)
    print("...Ожидание сообщений, для выхода нажмите CTRL+C")

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
