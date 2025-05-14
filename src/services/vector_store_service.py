from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import torch

client = PersistentClient(path="/data")
# EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
embeddings_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': _device})
vector_store = {}

def get_all_collections_id():
    return client.list_collections()

def inspect_collection(collection_id: str):
    collection = client.get_collection(collection_id)
    results = collection.get()
    return results

def get_vector_store(collection_name) -> Chroma:
    if collection_name not in vector_store:
        vector_store[collection_name] = Chroma(
            persist_directory="./data", 
            collection_name=collection_name,
            embedding_function=embeddings_function,
        )
    return vector_store[collection_name]

def add_documents(collection_name, documents):
    collection = get_vector_store(collection_name)
    collection.add_documents(documents)
    
def check_if_collection_exists(collection_id):
    try:
        client.get_collection(collection_id)
        return True
    except Exception as e:
        return False