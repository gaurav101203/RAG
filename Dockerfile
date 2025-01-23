# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir langchain_google_vertexai langchain_community langgraph nltk google-auth google-auth-oauthlib google-api-python-client google.cloud unstructured unstructured[pdf] gradio


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
