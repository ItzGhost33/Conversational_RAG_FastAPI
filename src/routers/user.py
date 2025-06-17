from fastapi import APIRouter, Depends, HTTPException, status
from src.models.schemas import UserCreate
from src.models.schemas import GetUserResponse, TokenData
from src.common.db import get_db, ApplicationLog, UserDetails, SessionStore
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter
from src.common.chat_logger import get_chat_history, get_or_create_active_session
from src.auth.hashing import get_password_hash
from src.auth.oauth2 import get_current_user
import hashlib



router = APIRouter()



@router.get('/user_history/{session_id}', status_code=status.HTTP_200_OK)
def get_user_by_session(
    session_id: str,
    db:Session = Depends(get_db),
):
    chat_history = get_chat_history(session_id,db)

    return {
        "session_id" : session_id,
        'history': chat_history
    }


@router.get('/all_users_history', status_code=status.HTTP_200_OK)
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



@router.post('/create_user', status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate,db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    existing_user = db.query(UserDetails).filter(
        (UserDetails.username == user.username) | (UserDetails.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    unique_string = f"{user.username.lower()}_{user.email.lower()}"
    user_id = hashlib.sha256(unique_string.encode()).hexdigest()
    
    new_user = UserDetails(
        user_id=user_id,
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        # "id": new_user.id,
        "user_id": new_user.user_id,
        "username": new_user.username,
        "email": new_user.email,
        "created_at": new_user.created_at
    }  



@router.get("/user/{username}", status_code=status.HTTP_200_OK,response_model=GetUserResponse)
def get_user_by_username(username: str, 
                         db: Session = Depends(get_db),
                         current_user: TokenData = Depends(get_current_user)
                         ):
    user = db.query(UserDetails).filter(UserDetails.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.user_id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }


@router.get("/user_sessions/{username}", status_code=status.HTTP_200_OK)
def get_user_sessions(
    username: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    # Ensure the requester is the same as the one whose data is being fetched
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(UserDetails).filter(UserDetails.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sessions = db.query(SessionStore).filter(SessionStore.username == user.username).order_by(SessionStore.created_at.desc()).all()

    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this user.")

    return {
        "user_id": user.user_id,
        "username": username,
        "session_ids": [
            {
                "session_id": s.session_id,
                "created_at": s.created_at,
                "is_active": s.is_active
            }
            for s in sessions
        ]
    }