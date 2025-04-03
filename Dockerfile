FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=UTC

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p web_app/static/uploads web_app/static/contributions web_app/database \
    && chmod -R 755 web_app/static/uploads web_app/static/contributions web_app/database

# Expose port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--chdir", "web_app", "--bind", "0.0.0.0:8080", "app:app"] 