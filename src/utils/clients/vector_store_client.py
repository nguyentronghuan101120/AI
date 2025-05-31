global persistent_client, embeddings_function


def load_vector_store_client():
    try:
        from chromadb import PersistentClient
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from constants.config import VECTOR_STORE_DIR, EMBEDDING_MODEL, TORCH_DEVICE
    except ImportError:
        raise ImportError(
            "chromadb, langchain_chroma, langchain_huggingface are not installed"
        )

    global persistent_client, embeddings_function
    persistent_client = PersistentClient(path=VECTOR_STORE_DIR)
    embeddings_function = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": TORCH_DEVICE},
    )
