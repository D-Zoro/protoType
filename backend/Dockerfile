
FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential gcc libpq-dev git curl && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY src ./src
COPY ./service_accounts ./service_accounts/
COPY ./.env .env

#  FastAPI port
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
