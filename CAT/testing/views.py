from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .cat_algorithm import CATAlgorithm3PL
from .forms import QuestionForm
from .models import Questions, Answers, TestQuestions, TestSessions, UserAnswers, Status

# Create your views here.

from django.shortcuts import render
from .models import Test, Questions, Topic


def index(request):
    tests = Test.objects.all()  # список всех тестов
    # authors = Users.objects.filter(role_id=2)
    return render(request, 'testing/index.html', {'tests': tests})



@login_required(login_url='login')
def questions_view(request):
    user = request.user

    # Проверка роли
    if not hasattr(user, 'role') or user.role.role_name != 'Преподаватель':
        messages.error(request, 'Доступ только для преподавателей.')
        return redirect('index')

    # Получаем вопросы с оптимизацией выборки
    questions = Questions.objects.select_related('topic', 'author').order_by('-question_id')

    # Пагинация по 20 вопросов
    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем список тем и форму для добавления вопроса
    topics = Topic.objects.all()
    form = QuestionForm()

    context = {
        'questions': page_obj,
        'topics': topics,
        'form': form
    }

    # Если AJAX-запрос — отрисовываем только часть контента (для "Показать ещё")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'testing/questions_list_partial.html', context)

    # Основной рендер всей страницы
    return render(request, 'testing/questions.html', context)

@login_required
def add_question(request):
    if not request.user.role or request.user.role.role_name != 'Преподаватель':
        return JsonResponse({"success": False, "error": "Только преподаватели могут добавлять вопросы."})

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        answers = request.POST.getlist('answer_text[]')
        correct_answer_index = request.POST.get('correct_answer')

        if form.is_valid() and answers:
            with transaction.atomic():
                question = form.save(commit=False)
                question.author = request.user
                question.save()

                for i, answer_text in enumerate(answers):
                    if not answer_text.strip():
                        continue
                    Answers.objects.create(
                        question=question,
                        answer_text=answer_text.strip(),
                        is_correct=str(i) == correct_answer_index,
                        answer_number=i + 1
                    )

            return JsonResponse({
                "success": True,
                "message": "Вопрос успешно добавлен",
                "question": question.text_question
            })
        else:
            return JsonResponse({"success": False, "error": "Некорректно заполнена форма."})

    return render(request, 'testing/questions.html')

@login_required
@require_http_methods(["DELETE"])
def delete_question(request, question_id):
    try:
        question = Questions.objects.get(pk=question_id)
        if question.author != request.user:
            return JsonResponse({"success": False, "error": "Вы не можете удалить этот вопрос."}, status=403)

        question.delete()
        return JsonResponse({"success": True})

    except Questions.DoesNotExist:
        return JsonResponse({"success": False, "error": "Вопрос не найден."}, status=404)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def create_test(request):
    if request.method == 'POST':
        test_name = request.POST.get('test_name')
        topic_id = request.POST.get('topic')

        if test_name and topic_id:
            topic = get_object_or_404(Topic, pk=topic_id)

            # Создаем тест
            test = Test.objects.create(
                test_name=test_name,
                topic=topic,
                author=request.user,
                num_of_questions=0
            )

            messages.success(request, f'Тест "{test_name}" успешно создан!')
            # Сразу перенаправляем на редактирование теста
            return redirect('edit_test', test_id=test.test_id)
        else:
            messages.error(request, 'Заполните все обязательные поля.')

    topics = Topic.objects.all()
    return render(request, 'testing/create_test.html', {
        'topics': topics
    })


@login_required
def edit_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)

    # Проверяем, что пользователь - автор теста
    if test.author != request.user:
        messages.error(request, 'Вы не можете редактировать этот тест.')
        return redirect('index')

    # Получаем вопросы по теме теста
    questions = Questions.objects.filter(topic=test.topic)

    # Получаем вопросы уже добавленные в тест
    test_questions = TestQuestions.objects.filter(test=test).select_related('question')

    # Обработка создания нового вопроса
    if request.method == 'POST' and 'text_question' in request.POST:
        form = QuestionForm(request.POST)
        answers = request.POST.getlist('answer_text[]')
        correct_answer_index = request.POST.get('correct_answer')

        if form.is_valid() and answers:
            with transaction.atomic():
                question = form.save(commit=False)
                question.author = request.user
                question.topic = test.topic  # Автоматически устанавливаем тему теста
                question.save()

                for i, answer_text in enumerate(answers):
                    if not answer_text.strip():
                        continue
                    Answers.objects.create(
                        question=question,
                        answer_text=answer_text.strip(),
                        is_correct=str(i) == correct_answer_index,
                        answer_number=i + 1
                    )

                # Автоматически добавляем новый вопрос в тест
                TestQuestions.objects.get_or_create(test=test, question=question)
                test.num_of_questions = TestQuestions.objects.filter(test=test).count()
                test.save()

            messages.success(request, 'Вопрос успешно создан и добавлен в тест!')
            return redirect('edit_test', test_id=test_id)
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = QuestionForm(initial={'topic': test.topic})  # Автозаполняем тему

    return render(request, 'testing/edit_test.html', {
        'test': test,
        'questions': questions,
        'test_questions': test_questions,
        'form': form
    })


@login_required
def add_question_to_test(request, test_id, question_id):
    test = get_object_or_404(Test, pk=test_id)
    question = get_object_or_404(Questions, pk=question_id)

    # Проверяем права доступа
    if test.author != request.user:
        messages.error(request, 'Вы не можете редактировать этот тест.')
        return redirect('index')

    # Добавляем вопрос в тест
    TestQuestions.objects.get_or_create(test=test, question=question)

    # Обновляем количество вопросов
    test.num_of_questions = TestQuestions.objects.filter(test=test).count()
    test.save()

    messages.success(request, f'Вопрос добавлен в тест "{test.test_name}"')
    return redirect('edit_test', test_id=test_id)


@login_required
def remove_question_from_test(request, test_id, question_id):
    test = get_object_or_404(Test, pk=test_id)
    question = get_object_or_404(Questions, pk=question_id)

    if test.author != request.user:
        messages.error(request, 'Вы не можете редактировать этот тест.')
        return redirect('index')

    # Удаляем вопрос из теста
    TestQuestions.objects.filter(test=test, question=question).delete()

    # Обновляем количество вопросов
    test.num_of_questions = TestQuestions.objects.filter(test=test).count()
    test.save()

    messages.success(request, 'Вопрос удален из теста')
    return redirect('edit_test', test_id=test_id)

###############################################################
@login_required
def start_adaptive_test(request, test_id):
    """Начало адаптивного тестирования"""
    test = get_object_or_404(Test, test_id=test_id)

    # Проверяем активную сессию
    active_session = TestSessions.objects.filter(
        user=request.user,
        test=test,
        status__status_name='in_progress'
    ).first()

    if active_session:
        return redirect('take_adaptive_test', session_id=active_session.session_id)

    # Получаем или создаем статусы
    in_progress_status, _ = Status.objects.get_or_create(status_name='in_progress')
    completed_status, _ = Status.objects.get_or_create(status_name='completed')

    # Создаем сессию тестирования
    with transaction.atomic():
        session = TestSessions.objects.create(
            user=request.user,
            test=test,
            current_ability_estimate=0.0,
            standard_error=1.0,
            status=in_progress_status,
            start_time=timezone.now()
        )

        # Выбираем первый вопрос
        available_questions = Questions.objects.filter(topic=test.topic)
        if available_questions.exists():
            cat = CATAlgorithm3PL()
            first_question = cat.select_next_question(0.0, list(available_questions), [])
            session.next_question = first_question
            session.save()

    return redirect('take_adaptive_test', session_id=session.session_id)


@login_required
def take_adaptive_test(request, session_id):
    """Страница прохождения адаптивного теста"""
    session = get_object_or_404(TestSessions, session_id=session_id, user=request.user)

    # Проверяем статус сессии
    if session.status.status_name == 'completed':
        return redirect('adaptive_test_results', session_id=session_id)

    current_question = session.next_question
    if not current_question:
        # Завершаем тест если нет следующего вопроса
        completed_status, _ = Status.objects.get_or_create(status_name='completed')
        session.status = completed_status
        session.end_time = timezone.now()
        session.save()
        return redirect('adaptive_test_results', session_id=session_id)

    # Получаем варианты ответов
    answers = Answers.objects.filter(question=current_question).order_by('answer_number')

    if request.method == 'POST':
        return handle_test_response(request, session, current_question, answers)

    context = {
        'session': session,
        'question': current_question,
        'answers': answers,
        'progress_percentage': min(100, (session.useranswers_set.count() / 30) * 100),
    }

    return render(request, 'testing/take_adaptive_test.html', context)


def handle_test_response(request, session, current_question, answers):
    """Обработка ответа пользователя"""
    selected_option = request.POST.get('selected_option')

    if not selected_option:
        messages.error(request, 'Пожалуйста, выберите вариант ответа')
        return redirect('take_adaptive_test', session_id=session.session_id)

    try:
        selected_option = int(selected_option)
        selected_answer = answers.get(answer_number=selected_option)

        # Проверяем правильность ответа
        correct_answer = answers.filter(is_correct=True).first()
        is_correct = (selected_answer == correct_answer)

        with transaction.atomic():
            # Сохраняем ответ пользователя
            user_answer = UserAnswers.objects.create(
                session=session,
                test=session.test,
                question=current_question,
                selected_answer=selected_answer,
                is_correct=is_correct,
                order_in_test=session.useranswers_set.count() + 1,
                answered_at=timezone.now()
            )

            # Получаем историю для пересчета theta
            user_answers = UserAnswers.objects.filter(session=session).select_related('question')
            response_history = [ua.is_correct for ua in user_answers]
            question_history = [ua.question for ua in user_answers]

            # Пересчитываем оценку способностей
            cat = CATAlgorithm3PL()
            current_theta = float(session.current_ability_estimate) if session.current_ability_estimate else 0.0

            new_theta, se = cat.estimate_ability(
                response_history,
                question_history,
                current_theta
            )

            # Рассчитываем вероятность правильного ответа для этого вопроса
            a = float(current_question.discrimination) if current_question.discrimination else 1.0
            b = float(current_question.difficulty) if current_question.difficulty else 0.0
            c = float(current_question.guessing) if current_question.guessing else 0.25
            probability = cat.probability_3pl(current_theta, a, b, c)

            # Обновляем user_answer
            user_answer.ability_after_answer = new_theta
            user_answer.standard_error_after = se
            user_answer.probability_of_correct = probability
            user_answer.save()

            # Обновляем сессию
            session.current_ability_estimate = new_theta
            session.standard_error = se

            # Проверяем критерий остановки
            theta_history = list(UserAnswers.objects.filter(
                session=session
            ).exclude(ability_after_answer=None).values_list(
                'ability_after_answer', flat=True
            ))

            should_stop, stop_reason = cat.should_stop_test(
                se,
                user_answers.count(),
                theta_history
            )

            if should_stop:
                completed_status, _ = Status.objects.get_or_create(status_name='completed')
                session.status = completed_status
                session.end_time = timezone.now()
                session.next_question = None
                session.save()
                return redirect('adaptive_test_results', session_id=session.session_id)
            else:
                # Выбираем следующий вопрос
                available_questions = Questions.objects.filter(topic=session.test.topic)
                next_question = cat.select_next_question(
                    new_theta,
                    list(available_questions),
                    question_history
                )
                session.next_question = next_question
                session.save()

                return redirect('take_adaptive_test', session_id=session.session_id)

    except Exception as e:
        messages.error(request, f'Ошибка при обработке ответа: {str(e)}')
        return redirect('take_adaptive_test', session_id=session.session_id)


@login_required
def adaptive_test_results(request, session_id):
    """Результаты адаптивного тестирования"""
    session = get_object_or_404(TestSessions, session_id=session_id, user=request.user)

    # Проверяем, что сессия завершена
    if session.status.status_name != 'completed':
        messages.warning(request, 'Тест еще не завершен!')
        return redirect('take_adaptive_test', session_id=session_id)

    # Статистика
    user_answers = UserAnswers.objects.filter(session=session).select_related(
        'question',
        'selected_answer',
        'question__correct_answer'
    )
    total_questions = user_answers.count()
    correct_answers = user_answers.filter(is_correct=True).count()

    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0

    # Уровень знаний по шкале theta
    theta = float(session.current_ability_estimate) if session.current_ability_estimate else 0.0
    standard_error = float(session.standard_error) if session.standard_error else 1.0

    # Определяем уровень знаний
    if theta >= 1.5:
        knowledge_level = "Экспертный"
        level_description = "Отличное понимание темы"
    elif theta >= 1.0:
        knowledge_level = "Продвинутый"
        level_description = "Хорошее понимание темы"
    elif theta >= 0.0:
        knowledge_level = "Средний"
        level_description = "Базовое понимание темы"
    elif theta >= -1.0:
        knowledge_level = "Начальный"
        level_description = "Ограниченное понимание темы"
    else:
        knowledge_level = "Новичок"
        level_description = "Требуется изучение основ"

    # Рассчитываем время прохождения
    if session.end_time and session.start_time:
        duration = session.end_time - session.start_time
        duration_minutes = duration.total_seconds() / 60
        duration_display = f"{int(duration_minutes)} мин {int(duration.total_seconds() % 60)} сек"
    else:
        duration_display = "Неизвестно"

    context = {
        'session': session,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy': round(accuracy, 1),
        'theta': round(theta, 3),
        'standard_error': round(standard_error, 3),
        'knowledge_level': knowledge_level,
        'level_description': level_description,
        'duration_display': duration_display,
        'user_answers': user_answers,
    }

    return render(request, 'testing/adaptive_test_results.html', context)


@login_required
def adaptive_test_list(request):
    """Список тестов для адаптивного тестирования"""
    tests = Test.objects.filter(testquestions__isnull=False).distinct()

    # Для преподавателей - их тесты, для студентов - все доступные
    if request.user.role.role_name == 'Преподаватель':
        tests = tests.filter(author=request.user)

    context = {
        'tests': tests,
    }

    return render(request, 'testing/adaptive_test_list.html', context)
