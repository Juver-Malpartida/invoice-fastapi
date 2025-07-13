# models.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class ApiTrackingLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4, index=True, unique=True)
    user_identifier: str
    filename: Optional[str] = None
    request_utc_timestamp: datetime = Field(default_factory=datetime.utcnow)
    completion_utc_timestamp: Optional[datetime] = None
    status: str = Field(default="PENDING") # PENDING, PROCESSING, COMPLETED, FAILED
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    error_message: Optional[str] = None
    final_json_response: Optional[str] = None # Almacenar el JSON como texto