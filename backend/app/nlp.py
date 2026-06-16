import re
from collections import Counter


COMMON_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "fastapi",
    "django",
    "flask",
    "spring",
    "machine learning",
    "nlp",
    "ocr",
    "data analysis",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "ci/cd",
    "git",
    "linux",
    "microservices",
    "rest",
    "graphql",
}

STOP_WORDS = {
    "and",
    "the",
    "for",
    "with",
    "from",
    "that",
    "this",
    "will",
    "are",
    "you",
    "our",
    "your",
    "have",
    "has",
    "was",
    "were",
    "can",
    "should",
    "into",
    "using",
    "role",
    "work",
    "team",
    "experience",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", normalize(text)) if token not in STOP_WORDS]


def extract_required_terms(job_description: str) -> set[str]:
    text = normalize(job_description)
    terms = {skill for skill in COMMON_SKILLS if skill in text}
    words = Counter(tokenize(job_description))
    terms.update(word for word, count in words.items() if count >= 2 and len(word) > 3)
    return terms


def rank_resume(resume_text: str, job_description: str) -> tuple[int, list[str]]:
    resume = normalize(resume_text)
    required_terms = extract_required_terms(job_description)

    if not required_terms:
        job_terms = set(tokenize(job_description))
        resume_terms = set(tokenize(resume_text))
        required_terms = {term for term in job_terms if len(term) > 3}
        matched = sorted(job_terms.intersection(resume_terms))
    else:
        matched = sorted(term for term in required_terms if term in resume)

    if not required_terms:
        return 0, []

    score = round((len(matched) / len(required_terms)) * 100)
    return min(score, 100), matched
