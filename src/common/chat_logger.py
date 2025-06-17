from src.common.db import SessionLocal, ApplicationLog, init_db
import uuid
from sqlalchemy.orm import Session
from src.common.db import SessionStore

# Ensure tables exist
init_db()

def insert_log(session_id, username, user_query, get_response,db):
    log = ApplicationLog(
        session_id=session_id,
        username=username,
        user_query=user_query,
        response=get_response
    )
    db.add(log)
    db.commit()

def get_chat_history(session_id, db):
    logs = db.query(ApplicationLog).filter_by(session_id=session_id).order_by(ApplicationLog.created_at.desc()).all()
    messages = []

    for row in logs:
        messages.extend([
            {"role": "user", "content": row.user_query},
            {"role": "ai", "content": row.response}
        ])
    
    return messages


def get_or_create_active_session(username: str, db: Session):
    # Check for an active session
    session = db.query(SessionStore).filter(
        SessionStore.username == username,
        SessionStore.is_active == "true"
    ).order_by(SessionStore.created_at.desc()).first()

    if session:
        return session.session_id

    # Else, create a new one
    new_session_id = str(uuid.uuid4())
    new_session = SessionStore(
        session_id=new_session_id,
        username=username
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session.session_id
