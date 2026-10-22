FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

ENV FLASK_PORT=5000
ENV FLASK_DEBUG=0
EXPOSE 5000

CMD ["python", "app.py"]
