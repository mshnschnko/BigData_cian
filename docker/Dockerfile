FROM python:3.11

WORKDIR /app

COPY ../app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../app .

CMD ["bash", "-c", "echo $DATABASE_URL && alembic upgrade head && python main.py"]