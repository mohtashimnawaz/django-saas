from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from courses.models import Lesson, Quiz, Question, Choice
from courses.tasks import generate_quiz_for_lesson

User = get_user_model()


class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher2", password="pass")
        self.course = None

    def test_generate_quiz_success(self):
        # Create course & lesson
        from courses.models import Course

        course = Course.objects.create(name="Science 101")
        lesson = Lesson.objects.create(course=course, title="Chemistry", content="Atoms and bonds", order=1)

        # Mock LLM response
        llm_response = {
            "questions": [
                {"text": f"Q{i}", "choices": ["A", "B", "C", "D"], "correct_index": 1} for i in range(1, 6)
            ]
        }

        with patch("courses.tasks.call_llm_generate_quiz", return_value=llm_response):
            quiz = generate_quiz_for_lesson(lesson.id, user_id=self.user.id)

        self.assertEqual(quiz.status, Quiz.STATUS_COMPLETED)
        self.assertEqual(quiz.questions.count(), 5)
        for q in quiz.questions.all():
            self.assertEqual(q.choices.count(), 4)
            self.assertEqual(q.choices.filter(is_correct=True).count(), 1)

    def test_generate_quiz_failure_sets_status(self):
        from courses.models import Course

        course = Course.objects.create(name="History 101")
        lesson = Lesson.objects.create(course=course, title="WW2", content="War facts", order=1)

        with patch("courses.tasks.call_llm_generate_quiz", side_effect=RuntimeError("LLM down")):
            with self.assertRaises(RuntimeError):
                generate_quiz_for_lesson(lesson.id, user_id=self.user.id)

        quiz = Quiz.objects.filter(lesson=lesson).first()
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.status, Quiz.STATUS_FAILED)
