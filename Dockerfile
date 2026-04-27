FROM python:3.11-slim

# Zuia Python isitengeneze .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Sakinisha vifaa vya mfumo vinavyohitajika
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Weka library za Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy kodi zote
COPY . /app/

# Gunicorn itawasha mradi live
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dozeeproject.wsgi:application"]