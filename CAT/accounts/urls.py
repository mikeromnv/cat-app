from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path("settings/", views.account_settings, name="account_settings"),
]
