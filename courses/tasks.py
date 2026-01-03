import os
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Lesson, Quiz, Question, Choice

LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")


def call_llm_generate_quiz(prompt: str) -> dict:
    """
    Generic wrapper around an LLM endpoint; returns a parsed structure:
    { "questions": [ { "text": "...", "choices": ["...","..."], "correct_index": 1 }, ... ] }
    For tests we will monkeypatch this function.
    """
    if not LLM_API_URL or not LLM_API_KEY:
        raise RuntimeError("LLM API not configured")
    # Import requests lazily so tests that mock this function don't need the dependency installed
    import requests
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_questions": 5}
    resp = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def generate_quiz_for_lesson(lesson_id, user_id=None, task_id=None):
    """Synchronous helper to generate a quiz for a lesson. Separated out for easy testing."""
    lesson = Lesson.objects.get(pk=lesson_id)
    quiz = Quiz.objects.create(
        lesson=lesson,
        created_by_id=user_id,
        status=Quiz.STATUS_GENERATING,
        celery_task_id=task_id,
    )

    try:
        prompt = (
            "Create 5 multiple choice questions (each with 4 choices) "
            "based on the following lesson content. Return JSON with keys: "
            "questions -> [ {text, choices: [..], correct_index } ]:\n\n"
            f"{lesson.content}"
        )
        data = call_llm_generate_quiz(prompt)
        questions = data.get("questions", [])[:5]
        for i, q in enumerate(questions, start=1):
            question = Question.objects.create(quiz=quiz, text=q["text"].strip(), order=i)
            for ctext_idx, ctext in enumerate(q["choices"]):
                Choice.objects.create(
                    question=question,
                    text=ctext.strip(),
                    is_correct=(ctext_idx == q.get("correct_index", 0)),
                )
        quiz.status = Quiz.STATUS_COMPLETED
        quiz.save()
        return quiz
    except Exception:
        quiz.status = Quiz.STATUS_FAILED
        quiz.save()
        raise


@shared_task(bind=True, name="generate_quiz_from_lesson")
def generate_quiz_from_lesson(self, lesson_id, user_id=None):
    return generate_quiz_for_lesson(lesson_id, user_id=user_id, task_id=self.request.id)
