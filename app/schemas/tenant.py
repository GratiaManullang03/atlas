from typing import List
from pydantic import BaseModel


class TenantCreate(BaseModel):
    schema_name: str


class TenantInfo(BaseModel):
    schema_name: str
    table_count: int
    created: bool


class TenantList(BaseModel):
    schemas: List[str]
    count: int
