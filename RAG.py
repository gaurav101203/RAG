# !pip install langchain_google_vertexai langchain_community langgraph nltk

# !pip install --upgrade google-auth google-auth-oauthlib google-api-python-client google.cloud

# !pip install unstructured unstructured[pdf] gradio

# !gcloud auth login          # Log In with your google cloud account

# !gcloud config set project project-ID         # Enter your project ID where Vertex AI API is enabled and have all the permissions

# !gcloud projects add-iam-policy-binding project-ID \
#     --member="serviceAccount:Service account email" \
#     --role="roles/aiplatform.user"

# Ensure your VertexAI credentials are configured
import os
import gradio as gr
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./GOOGLE_APPLICATION_CREDENTIALS.json"  #Upload your Google Cloud Service account(.json) key 


from google.oauth2 import service_account
from google.auth.transport.requests import Request

credentials = service_account.Credentials.from_service_account_file(
    "./GOOGLE_APPLICATION_CREDENTIALS.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(Request())

from google.cloud import aiplatform as vertexai

vertexai.init(
    project="project-ID",  # Replace with your Google Cloud project ID
    location="us-central1",
    credentials=credentials # Replace with your preferred region
)

# Choose the response generating model according to you
from langchain_google_vertexai import ChatVertexAI
llm = ChatVertexAI(model="gemini-1.5-pro-001")

# Choose the Embedding model according to you
from langchain_google_vertexai import VertexAIEmbeddings
embeddings = VertexAIEmbeddings(model="text-embedding-005")

from langchain_core.vectorstores import InMemoryVectorStore
vector_store = InMemoryVectorStore(embeddings)

import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

import bs4
from langchain import hub
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
import gradio as gr
import os
import shutil

# Define the directory to save uploaded files
UPLOAD_DIRECTORY = "./"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Save the file and then process it
def save_file(file):
    try:
        base_filename = os.path.basename(file.name)
        target_path = os.path.join(UPLOAD_DIRECTORY, base_filename)    # Define the target file path
        shutil.copy(file.name, target_path)
        DATA_PATH = "./"
        # Load and chunk contents of the documents
        loader = DirectoryLoader(
            DATA_PATH, glob="*.pdf"
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        _ = vector_store.add_documents(documents=all_splits)
        return f"File saved successfully"
    except Exception as e:
        return f"Error saving file: {str(e)}"
        
# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# Compile the above application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# Define the Interface for Question-Answering
def chatbot_interface(question):
    try:
        response = graph.invoke({"question": question})
        answer = response.get("answer", "No answer found.")
        return answer
    except Exception as e:
        return f"Error: {e}", None

# Gradio Interface
with gr.Blocks() as demo:
    with gr.Tab("Upload Files"):
        upload_file = gr.File(label="Upload PDF File")
        upload_output = gr.Textbox(label="Upload Status", interactive=False)
        upload_button = gr.Button("Upload and Process")

    with gr.Tab("Ask Questions"):
        question_input = gr.Textbox(label="Ask a Question")
        answer_output = gr.Textbox(label="Answer", interactive=False)
        question_button = gr.Button("Get Answer")
    upload_button.click(save_file, inputs=upload_file, outputs=upload_output)
    question_button.click(chatbot_interface, inputs=question_input, outputs=answer_output)
demo.launch()

