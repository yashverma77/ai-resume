from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None
    original_filename: str
    job_description: str
    extracted_text: str
    matched_skills: str
    score: int
    status: str
    error_message: str
    created_at: datetime
    updated_at: datetime
