# Use Python 3.10 as the base image for better performance and newer features
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Docker CLI (not Docker Engine)
RUN apt-get update && apt-get install -y \
    build-essential \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    git \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo \
        "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy alembic configuration and migrations
COPY alembic.ini .
COPY alembic/ ./alembic/

# Copy application code
COPY ./app ./app
COPY ./scripts ./scripts

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Create entrypoint script to handle different environments
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Create a non-root user and adjust ownership
RUN adduser --disabled-password --gecos '' nbforge \
    && chown -R nbforge:nbforge /app /docker-entrypoint.sh

# Switch to non-root user
USER nbforge

# Use entrypoint script to start the application
ENTRYPOINT ["/docker-entrypoint.sh"]

# Default to development mode - can be overridden in docker-compose or deployment
# see the entrypoint script for more details
CMD ["prod"]
