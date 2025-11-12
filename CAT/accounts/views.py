from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone

from .forms import RegisterForm
from .models import Users, UserRole

# ИСПРАВЛЕННЫЕ ИМПОРТЫ - убрать ..
try:
    from testing.models import TestSessions, UserAnswers, Topic

    TESTING_AVAILABLE = True
except ImportError as e:
    print(f"Testing models import error: {e}")
    TESTING_AVAILABLE = False


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна! Теперь войдите в систему.')
            return redirect('login')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    email_value = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        email_value = email  # сохраняем для формы

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверные данные для входа')

    return render(request, 'accounts/login.html', {'email_value': email_value})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def student_profile(request):
    """Профиль студента с статистикой"""
    user = request.user

    # Проверяем, что пользователь - студент
    if not hasattr(user, 'role') or not user.role or user.role.role_name != 'Студент':
        messages.error(request, 'Эта страница доступна только студентам.')
        return redirect('index')

    # Если testing модели недоступны
    if not TESTING_AVAILABLE:
        context = {
            'user': user,
            'total_tests': 0,
            'total_questions': 0,
            'total_correct': 0,
            'overall_accuracy': 0,
            'topics_progress': [],
            'recent_sessions': [],
            'testing_available': False
        }
        return render(request, 'accounts/student_profile.html', context)

    try:
        # Статистика по тестированиям
        test_sessions = TestSessions.objects.filter(
            user=user,
            status__status_name='completed'
        ).select_related('test', 'test__topic')

        # Общая статистика
        total_tests = test_sessions.count()
        total_questions = UserAnswers.objects.filter(session__user=user).count()
        total_correct = UserAnswers.objects.filter(session__user=user, is_correct=True).count()

        # Средняя точность
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

        # Прогресс по темам
        topics_progress = []
        topics = Topic.objects.all()

        for topic in topics:
            topic_sessions = test_sessions.filter(test__topic=topic)
            topic_tests = topic_sessions.count()

            if topic_tests > 0:
                # Средний theta по теме
                avg_theta_result = topic_sessions.aggregate(
                    avg_theta=Avg('current_ability_estimate')
                )
                avg_theta = avg_theta_result['avg_theta'] or 0

                # Лучший результат по теме
                best_session = topic_sessions.order_by('-current_ability_estimate').first()
                best_theta = best_session.current_ability_estimate if best_session else 0

                # Определяем уровень знаний
                if float(avg_theta) >= 1.5:
                    level = "Экспертный"
                elif float(avg_theta) >= 1.0:
                    level = "Продвинутый"
                elif float(avg_theta) >= 0.0:
                    level = "Средний"
                elif float(avg_theta) >= -1.0:
                    level = "Начальный"
                else:
                    level = "Новичок"

                topics_progress.append({
                    'topic': topic,
                    'tests_count': topic_tests,
                    'avg_theta': float(avg_theta),
                    'best_theta': float(best_theta) if best_theta else 0,
                    'level': level
                })

        # Последние тестирования
        recent_sessions = test_sessions.order_by('-end_time')[:5]

        context = {
            'user': user,
            'total_tests': total_tests,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'overall_accuracy': round(overall_accuracy, 1),
            'topics_progress': topics_progress,
            'recent_sessions': recent_sessions,
            'testing_available': True
        }

        return render(request, 'accounts/student_profile.html', context)

    except Exception as e:
        messages.error(request, f'Ошибка при загрузке профиля: {str(e)}')
        # Возвращаем базовый контекст при ошибке
        context = {
            'user': user,
            'total_tests': 0,
            'total_questions': 0,
            'total_correct': 0,
            'overall_accuracy': 0,
            'topics_progress': [],
            'recent_sessions': [],
            'testing_available': False
        }
        return render(request, 'accounts/student_profile.html', context)