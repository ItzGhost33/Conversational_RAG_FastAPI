from fastapi import Depends, HTTPException, status  
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data
    