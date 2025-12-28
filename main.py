from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.common.llm import llm_2
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.routers import authentication, user
from src.models.schemas import QueryRequest, RagResult, TokenData
from sqlalchemy.orm import Session
from fastapi import Depends, status
from src.common.chat_logger import get_or_create_active_session
from src.auth.oauth2 import get_current_user
from src.agentic_rag.rag import rag_service
from src.common.db import get_db, SessionStore





shared_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading LLM and Retriever...")

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    retriever = FAISS.load_local("faiss_index", embedding_model,allow_dangerous_deserialization=True).as_retriever()

    shared_state["llm"] = llm_2
    shared_state["retriever"] = retriever

    yield

    print("App shutdown — releasing resources")
 
app = FastAPI(lifespan=lifespan)
app.include_router(authentication.router, tags=["auth"])
app.include_router(user.router, tags=['user'])



@app.get("/")
def read_root():
    return {"message": "RAG API is running. Use POST /rag to query."}


@app.post("/rag", status_code = status.HTTP_200_OK, response_model=RagResult)
async def rag_endpoint(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    ):

    username = current_user.username or request.username
    session_id = get_or_create_active_session(username, db) or  request.session_id
    response,session_id, chat_history = rag_service(
        user_query=request.query,
        chat_history=[],
        # retriever=shared_state["retriever"],
        session_id=session_id,
        username=username,
        db = db
    )
    return {
        "answer": response,
        "session_id": session_id,
        "username": username
        # "history": chat_history
    }


@app.post("/end_session", status_code=status.HTTP_200_OK)
def end_session(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    session = db.query(SessionStore).filter(
        SessionStore.username == current_user.username,
        SessionStore.is_active == "true"
    ).order_by(SessionStore.created_at.desc()).first()

    if session:
        session.is_active = "false"
        db.commit()

    return {"detail": "Session ended"}



