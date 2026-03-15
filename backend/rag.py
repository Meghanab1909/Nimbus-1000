# rag.py
import os
import sys
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

FAISS_PATH = "vector_database"
FAISS_INDEX = os.path.join(FAISS_PATH, "index.faiss")
FAISS_PKL   = os.path.join(FAISS_PATH, "index.pkl")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def db_exists():
    return os.path.exists(FAISS_INDEX) and os.path.exists(FAISS_PKL)

def load_vectorstore():
    print(f"Loading existing vector store from {FAISS_PATH}...")
    return FAISS.load_local(FAISS_PATH, get_embeddings(), allow_dangerous_deserialization=True)

def save_vectorstore(db):
    os.makedirs(FAISS_PATH, exist_ok=True)
    db.save_local(FAISS_PATH)
    print(f"Vector store saved -> {FAISS_INDEX}, {FAISS_PKL}")

def ingest_files(file_paths: list[str]):
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} — file not found")
            continue
        print(f"Loading {file_path}...")
        loader = PyPDFLoader(file_path) if file_path.endswith(".pdf") else TextLoader(file_path)
        chunks = splitter.split_documents(loader.load())
        all_chunks.extend(chunks)
        print(f"  -> {len(chunks)} chunks")

    if not all_chunks:
        print("No chunks to ingest. Check that your files are .pdf or .txt")
        return

    if db_exists():
        print("Vector store found — adding documents...")
        db = load_vectorstore()
        db.add_documents(all_chunks)
    else:
        print("No vector store found — creating new one...")
        db = FAISS.from_documents(all_chunks, get_embeddings())

    save_vectorstore(db)
    print(f"Done. Total chunks ingested: {len(all_chunks)}")

def ingest_dir(folder_path: str):
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    supported = (".pdf", ".txt")
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(supported)
    ]

    print(f"Found {len(files)} file(s) in {folder_path}: {[os.path.basename(f) for f in files]}")

    if not files:
        print(f"No .pdf or .txt files found in {folder_path}")
        return

    ingest_files(files)

def query(question: str, k: int = 4):
    if not db_exists():
        print("No vector store found. Ingest some documents first.")
        return
    db = load_vectorstore()
    for i, doc in enumerate(db.similarity_search(question, k=k), 1):
        print(f"\n--- Result {i} ---\n{doc.page_content}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python rag.py ingest file1.pdf file2.txt ...")
        print("  python rag.py ingest-dir ./docs")
        print("  python rag.py query \"your question\"")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "ingest":
        ingest_files(sys.argv[2:])
    elif cmd == "ingest-dir":
        ingest_dir(sys.argv[2])
    elif cmd == "query":
        query(sys.argv[2])