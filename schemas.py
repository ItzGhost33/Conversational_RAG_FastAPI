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