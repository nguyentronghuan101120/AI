
import os
import uuid
import docx2txt
from PIL import Image
import pytesseract
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from constants.file_type import FileType
from services import vector_store_service

UPLOAD_DIR = "uploads"
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
    
def splitter_and_save_to_database(file_id, file_type, chat_session_id):
    try:
        file_content = get_file_content(file_id, file_type)
        splitted_file_content = data_splitter(file_content, file_id)
        vector_store_service.add_documents(chat_session_id, splitted_file_content)
        os.remove(os.path.join(UPLOAD_DIR, f"{file_id}.{file_type}"))
    except Exception as e:
        raise Exception(e)

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

def data_splitter(data, file_id):
    """
    Splits document data into smaller chunks and adds metadata.
    
    Args:
        data: The document data to split
        file_id: Unique identifier for the file
        
    Returns:
        List of document chunks with metadata and IDs
        
    The function:
    1. Creates a text splitter that breaks documents into 1000 char chunks with 200 char overlap
    2. Splits the input documents into chunks
    3. For each chunk:
        - Ensures it has a metadata dictionary
        - Adds the file_id to metadata
        - Generates a unique chunk ID using file_id and content
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Split into chunks of 1000 characters
        chunk_overlap=200, # Overlap chunks by 200 chars to maintain context
    )
    chunks = text_splitter.split_documents(data)
    for chunk in chunks:
        # Check if the chunk has a metadata attribute, if not create an empty dictionary
        if not hasattr(chunk, 'metadata'):
            chunk.metadata = {}
            
        # Add the file_id to the chunk's metadata to track which file it came from
        chunk.metadata['file_id'] = file_id
        
        # Generate a unique ID for this chunk by combining:
        # 1. The file_id (to group chunks from same file)
        # 2. The chunk's actual content (to make it content-specific)
        chunk_id_content = f"{file_id}-{chunk.page_content}"
        
        # Create a UUID (v5) using the combined string
        # UUID v5 generates a consistent UUID based on a namespace and a string
        # This ensures the same content always gets the same ID
        chunk.id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id_content))
    return chunks
