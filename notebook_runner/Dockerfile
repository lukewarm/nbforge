FROM ubuntu:22.04

# Disable interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies and clean up in the same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    git \
    libbz2-dev \
    libffi-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    libfribidi-dev \
    libgdal-dev \
    libgl1-mesa-glx \
    libharfbuzz-dev \
    liblzma-dev \
    libpcre3-dev \
    libreadline-dev \
    libssl-dev \
    zlib1g-dev

# Install python 3.12 from deadsnakes
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common \
        gnupg2 && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3.10-venv \
        python3.10-dev && \
    apt-get autoremove --purge -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*    

# Copy requirements and install all Python packages in a single layer
COPY requirements.txt /tmp/requirements.txt
COPY environments/py310-requirements.txt /tmp/environments/
COPY environments/py312-requirements.txt /tmp/environments/

# Create the main virtual environment
RUN \
    mkdir -p /opt/venv \
    && python3 -m venv --system-site-packages /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
    -r /tmp/requirements.txt

# Remove the default kernel
RUN /opt/venv/bin/jupyter kernelspec remove -y python3

# create unprivileged user to execute notebooks.
RUN useradd -m nbforge 

# Switch to the unprivileged user
USER nbforge 

# Create the Python 3.10 virtual environment and install it as a Jupyter kernel
RUN \
    mkdir /home/nbforge/venv310 \
    && python3.10 -m venv /home/nbforge/venv310 \
    && /home/nbforge/venv310/bin/pip install --no-cache-dir \
    -r /tmp/environments/py310-requirements.txt 

# Create the Python 3.12 virtual environment and install it as a Jupyter kernel
RUN \
    mkdir /home/nbforge/venv312 \
    && python3.12 -m venv /home/nbforge/venv312 \
    && /home/nbforge/venv312/bin/pip install --no-cache-dir \
    -r /tmp/environments/py312-requirements.txt 

USER root
RUN /home/nbforge/venv310/bin/python -m ipykernel install --name "python3.10" --display-name "Python 3.10"
RUN /home/nbforge/venv312/bin/python -m ipykernel install --name "python3.12" --display-name "Python 3.12"

# Copy application code
COPY src/ /home/nbforge/app/
RUN mkdir -p /notebooks /outputs
# Set ownership of the application code
RUN chown -R nbforge:nbforge /home/nbforge/app /notebooks /outputs

USER nbforge

ENV PYTHONPATH=/home/nbforge/app

WORKDIR /home/nbforge/app

# Set the entry point
ENTRYPOINT ["/opt/venv/bin/python3", "main.py"] 
