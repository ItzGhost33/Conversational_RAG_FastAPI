# Conversational RAG with FastAPI

This project implements a **Conversational Retrieval-Augmented Generation (RAG)** system using **FastAPI**. It allows users to ask natural language questions and receive intelligent, context-aware answers based on custom documents or data sources.

## 🚀 Features

- 🔍 Retrieval-Augmented Generation (RAG) pipeline
- 💬 Chat-based conversational interface
- ⚡ Built with FastAPI for high-performance APIs
- 🧠 Supports integration with LLMs (e.g., OpenAI, Groq, etc.)
- 🧾 Logging of user queries, responses, and session metadata
- 💾 SQLite for lightweight data storage



## 🧪 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ItzGhost33/Conversational_RAG_FastAPI.git
cd Conversational_RAG_FastAPI

```
### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI App
```bash
uvicorn main:app --reload

```