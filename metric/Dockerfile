# logs Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY metric/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY metric/src/ src/

CMD ["python", "src/metric.py"]
