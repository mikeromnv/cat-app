from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
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

# class Users(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
#     email = models.TextField(unique=True)
#     password = models.CharField(max_length=128, default='temp_password123')
#     username = models.CharField(max_length=100)
#     registration_date = models.DateTimeField(default=timezone.now)
#     num_group = models.IntegerField(blank=True, null=True)
#
#     def __str__(self):
#         return self.username
#
#     def set_password(self, raw_password):
#         self.password = make_password(raw_password)
#
#     def check_password(self, raw_password):
#         return check_password(raw_password, self.password)
#
#     class Meta:
#         db_table = 'users'

# class UserManager(BaseUserManager):
#     def create_user(self, email, username, password=None, role=None):
#         if not email:
#             raise ValueError("Email обязателен")
#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username, role=role)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, username, password=None):
#         user = self.create_user(email=email, username=username, password=password)
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user
#
#
# class Users(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=100)
#     full_name = models.CharField(max_length=200)
#     role = models.ForeignKey('UserRole', on_delete=models.SET_NULL, null=True, blank=True)
#     num_group = models.IntegerField(blank=True, null=True)
#     registration_date = models.DateTimeField(default=timezone.now)
#
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'email'  # логин через email
#     REQUIRED_FIELDS = ['username']
#
#     def __str__(self):
#         return self.username

