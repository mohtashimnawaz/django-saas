from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Lesson, Quiz
from .tasks import generate_quiz_from_lesson


@login_required
def dashboard(request):
    lessons = Lesson.objects.filter(course__teachers=request.user).select_related('course')
    return render(request, "courses/dashboard.html", {"lessons": lessons})


@login_required
@require_POST
def generate_quiz(request, lesson_pk):
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course__teachers=request.user)
    quiz = Quiz.objects.create(lesson=lesson, created_by=request.user, status=Quiz.STATUS_QUEUED)
    task = generate_quiz_from_lesson.delay(lesson.pk, request.user.pk)
    quiz.celery_task_id = task.id
    quiz.status = Quiz.STATUS_QUEUED
    quiz.save()
    return render(request, "courses/partials/quiz_button_fragment.html", {"quiz": quiz})


@login_required
def quiz_status(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, lesson__course__teachers=request.user)
    return render(request, "courses/partials/quiz_status_fragment.html", {"quiz": quiz})
