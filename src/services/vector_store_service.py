from constants.config import VECTOR_STORE_DIR, EMBEDDING_MODEL, TORCH_DEVICE
from utils.clients import vector_store_client


vector_store = {}


def get_all_collections_id():
    return vector_store_client.persistent_client.list_collections()


def inspect_collection(collection_id: str):
    collection = vector_store_client.persistent_client.get_collection(collection_id)
    results = collection.get()
    return results


def get_vector_store(collection_name) :
    if collection_name not in vector_store:
        vector_store[collection_name] = vector_store_client.chroma.Chroma(
            persist_directory=VECTOR_STORE_DIR,
            collection_name=collection_name,
            embedding_function=vector_store_client.embeddings_function,
        )
    return vector_store[collection_name]


def add_documents(collection_name, documents):
    collection = get_vector_store(collection_name)
    collection.add_documents(documents)


def check_if_collection_exists(collection_id):
    try:
        vector_store_client.persistent_client.get_collection(collection_id)
        return True
    except Exception as e:
        return False
