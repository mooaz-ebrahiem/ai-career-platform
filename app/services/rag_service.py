from app.rag.knowledge_base import index_resume
from app.rag.retriever import answer_resume_question


def add_resume_to_vector_db(resume_id: str, resume_text: str) -> dict:
    return index_resume(resume_id, resume_text)


def query_resume_rag(resume_id: str, query: str) -> dict:
    return answer_resume_question(resume_id, query)
