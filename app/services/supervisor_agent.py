from fastapi import HTTPException
from app.services.rag_service import add_resume_to_vector_db, query_resume_rag
from app.services.jop_service import match_resume_with_job


class SupervisorAgent:
    """
    الـ Supervisor Agent هو المسؤول عن استقبال طلبات المستخدم،
    تحليل نوع المهمة، وتوجيهها للخدمة (Agent) المختصة بدقة.
    """

    def __init__(self):
        print("Supervisor Agent initialized successfully! Ready to route tasks.")

    def route_task(self, task_type: str, payload: dict):
        """
        توجيه المهمة بناءً على نوع الـ Task المطلوب
        """
        if task_type == "index_resume":
            resume_id = payload.get("resume_id")
            resume_text = payload.get("resume_text")
            if not resume_id or not resume_text:
                raise HTTPException(status_code=400, detail="Missing resume_id or resume_text for indexing.")

            return add_resume_to_vector_db(resume_id=resume_id, resume_text=resume_text)

        elif task_type == "query_resume":
            resume_id = payload.get("resume_id")
            query = payload.get("query")
            if not resume_id or not query:
                raise HTTPException(status_code=400, detail="Missing resume_id or query.")

            return query_resume_rag(resume_id=resume_id, query=query)

        elif task_type == "match_job":
            resume_text = payload.get("resume_text")
            job_description = payload.get("job_description")
            if not resume_text or not job_description:
                raise HTTPException(status_code=400, detail="Missing resume_text or job_description.")

            return match_resume_with_job(
                resume_text=resume_text,
                job_description=job_description
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unknown task type: {task_type}. Supervisor cannot route this.")


supervisor = SupervisorAgent()