FROM python:3.12-slim

WORKDIR /app

# Optional system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy app dependencies from parent directory
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY ../server.py .

EXPOSE 8080

CMD ["python", "server.py"]