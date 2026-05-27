from pydantic import BaseModel


class SecurityRule(BaseModel):
    id: str
    description: str
    severity: str
