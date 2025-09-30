FROM python:3.11-slim

WORKDIR /app

# system deps (if you need to compile some packages)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

# copy requirements first to leverage layer caching
COPY requirements.txt .

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# default PORT (Cloud Run will override)
ENV PORT=8080
EXPOSE 8080

# start gunicorn on Cloud Run's port
ENTRYPOINT ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} main:app --workers 2"]
