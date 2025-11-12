from django.contrib import admin
from .models import *

# Простая регистрация моделей
admin.site.register(Topic)
admin.site.register(Questions)
admin.site.register(Answers)
admin.site.register(TestQuestions)
admin.site.register(Status)
admin.site.register(TestSessions)
admin.site.register(UserAnswers)