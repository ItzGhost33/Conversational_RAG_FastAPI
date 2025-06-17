from pydantic import BaseModel
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