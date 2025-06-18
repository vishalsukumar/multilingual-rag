import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from src.constants import DATA_DIR, VECTOR_STORE_PATH, OPENAI_EMBEDDINGS_MODEL


def load_pdfs(directory_path: str):
    """
    Load PDFs from a directory and split into chunks
    """
    # Load PDFs from directory
    loader = DirectoryLoader(
        directory_path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
    )
    
    chunks = text_splitter.split_documents(documents)
    return chunks


def initialize_vector_store():
    """
    Initialize the vector store with PDF chunks
    """
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)

    if not os.path.exists(VECTOR_STORE_PATH):
        pdf_chunks = load_pdfs(DATA_DIR)
        vectorstore = Chroma.from_documents(
            documents=pdf_chunks,
            embedding=embeddings,
            persist_directory=VECTOR_STORE_PATH,
        )
    else:
        vectorstore = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=embeddings,
        )
    return vectorstore
