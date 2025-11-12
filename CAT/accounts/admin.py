from django.contrib import admin
from .models import UserRole, Users

# Простая регистрация моделей
admin.site.register(UserRole)
admin.site.register(Users)