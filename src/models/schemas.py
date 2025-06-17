from pydantic import BaseModel, EmailStr
from typing import Optional 



class RagResult(BaseModel):
    answer: str

    class Config():
        orm_mode = True

class GetUserResponse(BaseModel):
    username : str
    email : str

    class Config():
        orm_mode = True
        

class Login(BaseModel):
    username : str
    password : str


class Token(BaseModel):
    access_token :  str
    token_type : str

class TokenData(BaseModel):
    username: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str]
    username: Optional[str]


class UserCreate(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    password: str