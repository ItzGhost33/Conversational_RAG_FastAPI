from db import SessionLocal, ApplicationLog, init_db

# Ensure tables exist
init_db()

def insert_log(session_id, user_query, get_response):
    db = SessionLocal()
    log = ApplicationLog(
        session_id=session_id,
        user_query=user_query,
        response=get_response
    )
    db.add(log)
    db.commit()
    db.close()

def get_chat_history(session_id):
    db = SessionLocal()
    logs = db.query(ApplicationLog).filter_by(session_id=session_id).order_by(ApplicationLog.created_at.desc()).all()
    messages = []

    for row in logs:
        messages.extend([
            {"role": "user", "content": row.user_query},
            {"role": "ai", "content": row.response}
        ])
    
    db.close()
    return messages
