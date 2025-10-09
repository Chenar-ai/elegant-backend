from typing import List, Optional
from pydantic import BaseModel



class CategoryTranslationSchema(BaseModel):
    language_code: str
    title: str
    intro: Optional[str] = None

    class Config:
        orm_mode = True


class CategoryCreateSchema(BaseModel):
    key: str
    references_json: Optional[str] = None
    translations: List[CategoryTranslationSchema]


class CategoryUpdateSchema(BaseModel):
    key: Optional[str] = None
    references_json: Optional[str] = None
    translations: Optional[List[CategoryTranslationSchema]] = None


class CategoryOutSchema(BaseModel):
    id: int
    key: str
    references_json: Optional[str]
    translations: List[CategoryTranslationSchema]

    class Config:
        orm_mode = True