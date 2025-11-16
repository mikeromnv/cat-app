from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class UserRole(models.Model):
    role_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.role_name

    class Meta:
        db_table = 'user_role'


class Users(AbstractUser):
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True)
    num_group = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    registration_date = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'  # аутентификация по email
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'