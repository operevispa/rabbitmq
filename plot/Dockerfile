# plot Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY plot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY plot/src/ src/

CMD ["python", "src/plot.py"]
