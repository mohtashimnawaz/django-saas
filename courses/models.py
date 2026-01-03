from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="courses")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} — {self.title}"


class Quiz(models.Model):
    STATUS_PENDING = "pending"
    STATUS_QUEUED = "queued"
    STATUS_GENERATING = "generating"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_QUEUED, "Queued"),
        (STATUS_GENERATING, "Generating"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="quizzes")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Quiz for {self.lesson} ({self.status})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=1024)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:60]}"
