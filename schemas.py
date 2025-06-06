from pydantic import BaseModel
from typing import Optional 




class RagResult(BaseModel):
    answer: str

    class Config():
        orm_mode = True