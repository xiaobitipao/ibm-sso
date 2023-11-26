FROM python:3.11.6-slim-bookworm

# Install needed environment
RUN apt-get -y update; apt-get -y install libpq-dev gcc

RUN python -m pip install --upgrade pip

# Set directory
WORKDIR /app

# Install mudules
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Create custom modeles folder
RUN mkdir -p api/v1

# Copy source
COPY app.py .
COPY api ./api

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
