from pydantic import BaseModel
from typing import Optional, List


class GuidelineBase(BaseModel):
    text: str
    text_hi: Optional[str] = None
    icon_type: str = "check"
    severity: str = "#e8f5e9"
    sort_order: int = 0
    is_active: bool = True


class GuidelineCreate(GuidelineBase):
    pass


class GuidelineUpdate(BaseModel):
    text: Optional[str] = None
    text_hi: Optional[str] = None
    icon_type: Optional[str] = None
    severity: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class GuidelineResponse(GuidelineBase):
    id: int

    class Config:
        from_attributes = True


class BulkGuidelineUpdate(BaseModel):
    guidelines: List[GuidelineCreate]
