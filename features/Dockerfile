# features Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY features/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY features/src/ src/

CMD ["python", "src/features.py"]