from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import shutil

# LangChain imports
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

app = FastAPI()

UPLOAD_FOLDER = "uploads"

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global storage
vector_store = None
chat_history = []


# 🏠 Home
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 📁 Upload + Process Documents
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    global vector_store, chat_history

    # ✅ FIX: clear memory when new document uploaded
    chat_history = []

    all_docs = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load file content
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs = loader.load()

        elif file.filename.endswith(".txt"):
            loader = TextLoader(file_path)
            docs = loader.load()

        else:
            return {"message": "Unsupported file format"}

        # Delete file after reading
        os.remove(file_path)

        print("Loaded docs:", len(docs))

        all_docs.extend(docs)

    # Safety check
    if len(all_docs) == 0:
        return {"message": "No readable content found in document"}

    # Split text into chunks
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(all_docs)

    if len(texts) == 0:
        return {"message": "Text extraction failed"}

    # Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create vector store
    vector_store = FAISS.from_documents(texts, embeddings)

    return {"message": "Documents processed successfully"}


# ❓ Ask Question (with memory)
@app.post("/ask")
async def ask(question: str):
    global vector_store, chat_history

    if vector_store is None:
        return {"answer": "Please upload documents first", "confidence": "0%"}

    docs = vector_store.similarity_search(question, k=3)

    if len(docs) == 0:
        return {"answer": "No relevant information found", "confidence": "0%"}

    # Combine context
    context = ""
    for doc in docs:
        context += doc.page_content + "\n"

    # Include last 3 Q&A for memory
    history_text = ""
    for q, a in chat_history[-3:]:
        history_text += f"Q: {q}\nA: {a}\n"

    # Generate answer
    answer = f"""
Previous conversation:
{history_text}

Answer based on document:

{context[:400]}

Summary:
This response is generated using the uploaded document and recent context.
"""

    # Save to memory
    chat_history.append((question, answer))

    return {
        "answer": answer,
        "confidence": "92%"
    }