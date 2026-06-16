import logging
import time
from pathlib import Path

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.extractor import extract_text
from app.models import Candidate
from app.nlp import rank_resume

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("resume-worker")


def process_once() -> int:
    settings = get_settings()
    processed = 0
    with SessionLocal() as db:
        candidates = db.scalars(
            select(Candidate).where(Candidate.status == "queued").order_by(Candidate.created_at).limit(5)
        ).all()

        for candidate in candidates:
            candidate.status = "processing"
            candidate.error_message = ""
            db.commit()

            try:
                path = Path(settings.upload_dir) / candidate.stored_filename
                text = extract_text(path)
                score, matched = rank_resume(text, candidate.job_description)
                candidate.extracted_text = text[:20000]
                candidate.score = score
                candidate.matched_skills = ", ".join(matched)
                candidate.status = "completed"
                logger.info("Processed candidate id=%s score=%s", candidate.id, score)
            except Exception as exc:
                candidate.status = "failed"
                candidate.error_message = str(exc)
                logger.exception("Failed candidate id=%s", candidate.id)
            finally:
                db.commit()
                processed += 1

    return processed


def main() -> None:
    settings = get_settings()
    init_db()
    logger.info("Worker service started")
    while True:
        count = process_once()
        if count == 0:
            time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
