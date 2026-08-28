from pydantic import BaseModel


class SessionCreate(BaseModel):
    model: str