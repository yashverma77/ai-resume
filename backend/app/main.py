import logging
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db, init_db
from app.models import Candidate
from app.schemas import CandidateOut

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("resume-api")

app = FastAPI(title="AI Resume Screening API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


@app.on_event("startup")
def startup() -> None:
    init_db()
    logger.info("API service started")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/resumes", response_model=CandidateOut, status_code=201)
async def upload_resume(
    name: str = Form(...),
    email: str | None = Form(None),
    job_description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Candidate:
    settings = get_settings()
    original = file.filename or "resume"
    suffix = Path(original).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File is larger than {settings.max_upload_mb} MB")

    stored_filename = f"{uuid4().hex}{suffix}"
    destination = settings.upload_dir / stored_filename
    destination.write_bytes(content)

    candidate = Candidate(
        name=name.strip(),
        email=email.strip() if email else None,
        original_filename=original,
        stored_filename=stored_filename,
        job_description=job_description.strip(),
        status="queued",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    logger.info("Queued resume id=%s file=%s", candidate.id, original)
    return candidate


@app.get("/candidates", response_model=list[CandidateOut])
def list_candidates(db: Session = Depends(get_db)) -> list[Candidate]:
    return db.query(Candidate).order_by(desc(Candidate.score), desc(Candidate.created_at)).all()


@app.get("/candidates/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
