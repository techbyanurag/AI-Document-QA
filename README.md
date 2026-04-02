# 🧠 AI Document Question Answering System

A modern AI-powered web application that allows users to upload documents and ask questions based on their content.

---

## 🚀 Features

- 📁 Upload multiple documents (PDF, TXT)
- 🔍 Intelligent document search using embeddings
- 💬 Ask questions and get contextual answers
- ⚡ Fast retrieval using FAISS vector database
- 🧠 Smart summarization of document content
- 🎯 Confidence score for responses
- 🌙 Premium dark-themed UI

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **AI/NLP:** LangChain, HuggingFace Embeddings
- **Vector DB:** FAISS
- **Other:** PyPDF, Python-Docx

---

## 📂 Project Structure
AI-Document-QA/
│
├── app.py
├── requirements.txt
│
├── static/
│ ├── style.css
│ └── script.js
│
├── templates/
│ └── index.html

---

## ⚙️ Installation & Setup

### 1. Clone the repository
git clone https://github.com/techbyanurag/AI-Document-QA.git
cd AI-Document-QA

---

### 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate



---

### 3. Install dependencies
pip install -r requirements.txt



---

### 4. Run the server
python -m uvicorn app:app --reload



---

### 5. Open in browser
http://127.0.0.1:8000

---

## 📌 How to Use

1. Upload a document (PDF or TXT)
2. Wait for processing
3. Ask a question related to the document
4. View the AI-generated answer

---

## 🎨 UI Design

- Premium dark theme
- Glassmorphism effects
- Minimalist layout
- Smooth user experience

---

## ⚠️ Notes

- Do not upload large unnecessary files (like venv)
- Works best with text-based documents

---


## 📄 License

This project is for educational and demonstration purposes.
