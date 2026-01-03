from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, Mock

from courses.models import Course, Lesson, Quiz

User = get_user_model()


class HTMXViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher3", password="pass")
        self.course = Course.objects.create(name="Eng 101")
        self.course.teachers.add(self.user)
        self.lesson = Lesson.objects.create(course=self.course, title="Intro", content="Hello", order=1)

    def test_generate_quiz_htmx_post_enqueues_task(self):
        self.client.login(username="teacher3", password="pass")
        url = reverse("courses:generate_quiz", args=[self.lesson.pk])
        mock_task = Mock()
        mock_task.id = "celery-abc"
        with patch("courses.views.generate_quiz_from_lesson.delay", return_value=mock_task) as p:
            resp = self.client.post(url, HTTP_HX_REQUEST="true")

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Queued")
        quiz = Quiz.objects.filter(lesson=self.lesson).first()
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.celery_task_id, "celery-abc")
        self.assertEqual(quiz.status, Quiz.STATUS_QUEUED)

    def test_quiz_status_polling_shows_completed(self):
        self.client.login(username="teacher3", password="pass")
        quiz = Quiz.objects.create(lesson=self.lesson, created_by=self.user, status=Quiz.STATUS_COMPLETED)
        url = reverse("courses:quiz_status", args=[quiz.pk])
        resp = self.client.get(url, HTTP_HX_REQUEST="true")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "View Quiz")
