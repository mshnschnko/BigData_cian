FROM python:3.11

WORKDIR /kafkahandler

COPY ../kafkahandler/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../kafkahandler .

CMD ["python", "main.py"]