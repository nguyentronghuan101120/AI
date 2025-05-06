from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

client = PersistentClient(path="./data")
EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
collections = client.list_collections()

def get_all_collections_id():
    return collections

def inspect_collection(collection_id: str):
    collection = client.get_collection(collection_id)
    results = collection.get()
    return results

def get_vector_store(collection_name):
    return Chroma(
    persist_directory="./data", 
    collection_name=collection_name,
    embedding_function=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL),
    )

def add_documents(collection_name, documents):
    collection = get_vector_store(collection_name)
    collection.add_documents(documents)
    
def check_if_collection_exists(collection_id):
    return get_vector_store(collection_id) is not None