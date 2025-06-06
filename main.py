from fastapi import FastAPI
from contextlib import asynccontextmanager
from rag import rag_service
from llm import llm
from pydantic import BaseModel
from typing import Optional  
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from schemas import RagResult
from db import get_db, ApplicationLog
from sqlalchemy.orm import Session
from fastapi import Depends, status
from chat_logger import get_chat_history



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


@app.get("/")
def read_root():
    return {"message": "RAG API is running. Use POST /rag to query."}



class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str]



@app.get('/user_history/{session_id}', status_code=status.HTTP_200_OK)
def get_user_by_session(
    session_id: str,
    db:Session = Depends(get_db),
):
    chat_history = get_chat_history(session_id,db)

    return {
        "session_id" : session_id,
        'history': chat_history
    }
    


@app.get('/all_users_history', status_code=status.HTTP_200_OK)
def get_all_user_histories(db: Session = Depends(get_db)):
    logs = db.query(ApplicationLog).order_by(ApplicationLog.created_at.desc()).all()
    
    all_histories = {}
    for row in logs:
        session_id = row.session_id
        if session_id not in all_histories:
            all_histories[session_id] = []
        all_histories[session_id].append(
            {"role": "user", "content": row.user_query}
        )
        all_histories[session_id].append(
            {"role": "ai", "content": row.response}
        )
    
    return all_histories



@app.post("/rag", status_code = status.HTTP_201_CREATED, response_model=RagResult)
async def rag_endpoint(
    request: QueryRequest,
    db: Session = Depends(get_db),
    ):

    session_id = request.session_id or "anonymous"
    response,session_id, chat_history = rag_service(
        user_query=request.query,
        chat_history=[],
        retriever=shared_state["retriever"],
        session_id=session_id,
        db = db
    )
    return {
        "answer": response,
        "session_id": session_id,
        # "history": chat_history
    }

