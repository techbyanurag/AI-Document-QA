from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import shutil

# LangChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Local LLM (NO API)
from transformers import pipeline

app = FastAPI()

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

vector_store = None

# 🔥 Load local GenAI model (first time will download ~1-2GB)
generator = pipeline("text2text-generation", model="google/flan-t5-base")


# 🏠 Home
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 📁 Upload
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    global vector_store

    all_docs = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            os.remove(file_path)

        elif file.filename.endswith(".txt"):
            loader = TextLoader(file_path)
            docs = loader.load()
            os.remove(file_path)

        else:
            return {"message": "Unsupported file format"}

        all_docs.extend(docs)

    if len(all_docs) == 0:
        return {"message": "No content found"}

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(all_docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Reset for new docs
    vector_store = FAISS.from_documents(texts, embeddings)

    return {"message": "Documents processed successfully"}


# ❓ Ask (LOCAL GEN AI)
@app.post("/ask")
async def ask(question: str):
    global vector_store

    if vector_store is None:
        return {"answer": "Upload document first", "confidence": "0%"}

    docs = vector_store.similarity_search(question, k=3)

    if len(docs) == 0:
        return {"answer": "No relevant info found", "confidence": "0%"}

    context = "\n".join([doc.page_content for doc in docs])

    # 🔥 Prompt for GenAI
    prompt = f"""
    Answer the question based only on the context below.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    result = generator(prompt, max_length=200, do_sample=False)

    answer = result[0]["generated_text"]

    confidence = f"{min(90, 60 + len(docs)*10)}%"
    sources = [doc.page_content[:120] for doc in docs]

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources
    }


# 📊 Summarize
@app.post("/summarize")
async def summarize():
    global vector_store

    if vector_store is None:
        return {"summary": "Upload documents first"}

    docs = vector_store.similarity_search("", k=5)
    text = " ".join([d.page_content for d in docs])[:1500]

    prompt = f"Summarize this:\n{text}"

    result = generator(prompt, max_length=150, do_sample=False)

    return {"summary": result[0]["generated_text"]}
