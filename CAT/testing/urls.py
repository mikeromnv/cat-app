from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('login/', auth_views.LoginView.as_view(), name='login'),

    path('questions/', views.questions_view, name='questions'),
    path('add-question/', views.add_question, name='add_question'),
    path('create_test/', views.create_test, name='create_test'),
    path('edit-test/<int:test_id>/', views.edit_test, name='edit_test'),
    path('add-question-to-test/<int:test_id>/<int:question_id>/', views.add_question_to_test,
         name='add_question_to_test'),
    path('remove-question-from-test/<int:test_id>/<int:question_id>/', views.remove_question_from_test,
         name='remove_question_from_test'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    # path('get_question_data/<int:question_id>/', views.get_question_data, name='get_question_data'),
    # path('update_question/<int:question_id>/', views.update_question, name='update_question'),


    path('adaptive-tests/', views.adaptive_test_list, name='adaptive_test_list'),
    path('start-adaptive-test/<int:test_id>/', views.start_adaptive_test, name='start_adaptive_test'),
    path('take-adaptive-test/<int:session_id>/', views.take_adaptive_test, name='take_adaptive_test'),
    path('adaptive-test-results/<int:session_id>/', views.adaptive_test_results, name='adaptive_test_results'),

    path('get_test_statistics/<int:session_id>/', views.get_test_statistics, name='get_test_statistics'),

    path("my_tests/", views.my_tests, name="my_tests"),
    path("delete_test/<int:test_id>/", views.delete_test, name="delete_test"),
    path("test/<int:test_id>/", views.view_test, name="view_test"),
    # path('teacher_test_stats/<int:session_id>/', views.teacher_test_stats, name='teacher_test_stats'),





]