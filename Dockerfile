FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install pip requirements
RUN pip install langchain_google_vertexai langchain_community langgraph nltk google-auth google-auth-oauthlib google-api-python-client google.cloud unstructured unstructured[pdf] gradio

WORKDIR /app
COPY . /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 7860
CMD ["python", "RAG.py"]
