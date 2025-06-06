from fastapi import FastAPI
from contextlib import asynccontextmanager
from rag import rag_service
from llm import llm
from pydantic import BaseModel,EmailStr
from typing import Optional  
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from schemas import RagResult, GetUserResponse
from db import get_db, ApplicationLog, UserDetails
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from chat_logger import get_chat_history
from passlib.context import CryptContext



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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@app.get("/")
def read_root():
    return {"message": "RAG API is running. Use POST /rag to query."}



class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str]


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str



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


@app.post('/create_user', status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate,db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    existing_user = db.query(UserDetails).filter(
        (UserDetails.username == user.username) | (UserDetails.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    new_user = UserDetails(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "created_at": new_user.created_at
    }  



@app.get("/user/{username}", status_code=status.HTTP_200_OK,response_model=GetUserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(UserDetails).filter(UserDetails.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }




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

