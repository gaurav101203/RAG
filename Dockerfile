# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install GDAL dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the path for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
# Install system-level dependencies
# Install system-level dependencies, including R
RUN apt-get update && apt-get install -y \
    r-base \
    libcairo2-dev \
    libxt-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    pkg-config \
    gcc \
    g++ \
    && apt-get clean

# Set R_HOME and PATH environment variables
ENV R_HOME=/usr/lib/R
ENV PATH=$PATH:/usr/lib/R/bin

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /app
COPY . /app

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/rag-model-448019-7622d30ebd3b.json

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 7860
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "RAG.py"]
