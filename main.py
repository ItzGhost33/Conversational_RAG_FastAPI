from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from rag import rag_service
from llm import llm  
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from typing import Optional


shared_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading LLM and Retriever...")

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    retriever = FAISS.load_local("faiss_index", embedding_model,allow_dangerous_deserialization=True).as_retriever()

    shared_state["llm"] = llm
    shared_state["retriever"] = retriever

    yield

    print("App shutdown — releasing resources")

app = FastAPI(lifespan=lifespan)

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str]


@app.get("/")
def read_root():
    return {"message": "RAG API is running. Use POST /rag to query."}

@app.post("/rag")
async def rag_endpoint(request: QueryRequest):
    session_id = request.session_id or "anonymous"
    response,session_id, chat_history = rag_service(
        user_query=request.query,
        chat_history=[],
        retriever=shared_state["retriever"],
        session_id=session_id
    )
    return {
        "answer": response,
        "session_id": session_id,
        "history": chat_history
    }

