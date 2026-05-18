# 1. Base image
FROM python:3.11-slim

# 2. Set environment variables
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Change directory to the django project root where manage.py is located
WORKDIR /app/diet_recommendation

# 8. Expose port 8000
EXPOSE 8000

# 9. Run migrations and start application using Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 diet_recommendation.wsgi:application"]
