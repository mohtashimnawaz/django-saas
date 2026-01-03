from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("lesson/<int:lesson_pk>/generate-quiz/", views.generate_quiz, name="generate_quiz"),
    path("quiz/<int:quiz_pk>/status/", views.quiz_status, name="quiz_status"),
]
