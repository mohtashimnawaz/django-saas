from django.test import TestCase
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson, Quiz, Question, Choice

User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher1", password="pass")
        self.course = Course.objects.create(name="Math 101", description="Intro to Math")
        self.course.teachers.add(self.user)

    def test_course_str(self):
        self.assertEqual(str(self.course), "Math 101")

    def test_lesson_creation(self):
        lesson = Lesson.objects.create(course=self.course, title="Lesson 1", content="Content of lesson 1", order=1)
        self.assertEqual(lesson.course, self.course)
        self.assertEqual(lesson.title, "Lesson 1")
        self.assertEqual(lesson.order, 1)

    def test_quiz_question_choice_creation(self):
        lesson = Lesson.objects.create(course=self.course, title="Lesson 2", content="Content for quiz", order=2)
        quiz = Quiz.objects.create(lesson=lesson, created_by=self.user, status=Quiz.STATUS_PENDING)
        q1 = Question.objects.create(quiz=quiz, text="What is 2+2?", order=1)
        Choice.objects.create(question=q1, text="3", is_correct=False)
        Choice.objects.create(question=q1, text="4", is_correct=True)
        Choice.objects.create(question=q1, text="5", is_correct=False)
        Choice.objects.create(question=q1, text="22", is_correct=False)

        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(q1.choices.count(), 4)
        correct_choices = q1.choices.filter(is_correct=True)
        self.assertEqual(correct_choices.count(), 1)
        self.assertEqual(correct_choices.first().text, "4")

    def test_question_str(self):
        lesson = Lesson.objects.create(course=self.course, title="Lesson 3", content="Another", order=3)
        quiz = Quiz.objects.create(lesson=lesson, created_by=self.user)
        q = Question.objects.create(quiz=quiz, text="Q text", order=1)
        self.assertIn("Q1", str(q))

    def test_choice_str(self):
        lesson = Lesson.objects.create(course=self.course, title="Lesson 4", content="Another", order=4)
        quiz = Quiz.objects.create(lesson=lesson, created_by=self.user)
        q = Question.objects.create(quiz=quiz, text="Q text", order=1)
        c = Choice.objects.create(question=q, text="C text", is_correct=True)
        self.assertIn("✓", str(c))
