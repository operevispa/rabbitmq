# model Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY model/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model/src/ src/

CMD ["python", "src/model.py"]
