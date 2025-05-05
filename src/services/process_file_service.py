
import os
import uuid
import docx2txt
from PIL import Image
from langchain_chroma import Chroma
import pytesseract
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from constants.file_type import FileType

UPLOAD_DIR = "uploads"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file):
    ext = os.path.splitext(file.filename)[-1].lstrip(".")
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_id, ext

def get_file_content(file_id, file_type: FileType):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_type}")

    if file_type == FileType.pdf:
        return extract_pdf(file_path)
    elif file_type == FileType.docx:
        return extract_docx(file_path)
    elif file_type == FileType.image:
        return extract_image(file_path)
    elif file_type == FileType.video:
        return {"note": "Video processing not yet implemented."}
    
def splitter_and_save_to_database(file_id, file_type):
    try:
        file_content = get_file_content(file_id, file_type)
        splitted_file_content = data_splitter(file_content)
        
        vector_store = get_vector_store(file_id)
        vector_store.add_documents(splitted_file_content)
        os.remove(os.path.join(UPLOAD_DIR, f"{file_id}.{file_type}"))
    except Exception as e:
        raise Exception(f"File already processed or not exists {str(e)}")

def extract_pdf(path):
    loader = PyMuPDFLoader(path)
    docs = loader.load()
    return docs

def extract_docx(path):
    text = docx2txt.process(path)
    return {"type": "docx", "text": text}

def extract_image(path):
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return {"type": "image", "text": text}

def data_splitter(data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  
        chunk_overlap=200, 
    )
    chunks = text_splitter.split_documents(data)
    for chunk in chunks:
        chunk.id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.page_content))
    return chunks

def get_vector_store(collection_name):
    return Chroma(
    persist_directory="./data", 
    collection_name=collection_name,
    embedding_function=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL),
    )