from pydantic import BaseModel

class IHelloDto(BaseModel):
    message: str