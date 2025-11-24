# accounts/populate_db.py

from django.utils import timezone
from accounts.models import Users, UserRole
from testing.models import Topic, Questions, Answers, Test, TestQuestions

def run():
    print("=== Начало заполнения БД тестовыми данными ===")

    # --- Роли ---
    student_role, _ = UserRole.objects.get_or_create(role_name='Студент')
    teacher_role, _ = UserRole.objects.get_or_create(role_name='Преподаватель')
    print("Роли созданы")

    # --- Пользователи ---
    teacher, _ = Users.objects.get_or_create(
        username='teacher1',
        email='teacher1@example.com',
        defaults={
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'role': 'Преподаватель',
            'is_staff': True,
            'is_superuser': True,
            'registration_date': timezone.now(),
        }
    )
    teacher.set_password('teacher123')
    teacher.save()

    student1, _ = Users.objects.get_or_create(
        username='student1',
        email='student1@example.com',
        defaults={
            'first_name': 'Петр',
            'last_name': 'Петров',
            'role': student_role,
            'num_group': 101,
            'registration_date': timezone.now(),
        }
    )
    student1.set_password('student123')
    student1.save()

    student2, _ = Users.objects.get_or_create(
        username='student2',
        email='student2@example.com',
        defaults={
            'first_name': 'Анна',
            'last_name': 'Сидорова',
            'role': student_role,
            'num_group': 102,
            'registration_date': timezone.now(),
        }
    )
    student2.set_password('student123')
    student2.save()

    print("Пользователи созданы")

    # --- Темы ---
    math_topic, _ = Topic.objects.get_or_create(
        topic_name='Математика', defaults={'description': 'Тесты по математике'}
    )
    physics_topic, _ = Topic.objects.get_or_create(
        topic_name='Физика', defaults={'description': 'Тесты по физике'}
    )
    print("Темы созданы")

    # --- Вопросы и ответы ---
    q1, _ = Questions.objects.get_or_create(
        text_question='Сколько будет 2 + 2?',
        topic=math_topic,
        author=teacher,
        defaults={'difficulty': 0.1}
    )
    a1_q1, _ = Answers.objects.get_or_create(question=q1, answer_number=1, answer_text='3', is_correct=False)
    a2_q1, _ = Answers.objects.get_or_create(question=q1, answer_number=2, answer_text='4', is_correct=True)
    a3_q1, _ = Answers.objects.get_or_create(question=q1, answer_number=3, answer_text='5', is_correct=False)
    q1.correct_answer = a2_q1
    q1.save()

    q2, _ = Questions.objects.get_or_create(
        text_question='Сила тяжести на Земле?',
        topic=physics_topic,
        author=teacher,
        defaults={'difficulty': 0.2}
    )
    a1_q2, _ = Answers.objects.get_or_create(question=q2, answer_number=1, answer_text='9.8 м/с²', is_correct=True)
    a2_q2, _ = Answers.objects.get_or_create(question=q2, answer_number=2, answer_text='10 м/с²', is_correct=False)
    q2.correct_answer = a1_q2
    q2.save()

    print("Вопросы и ответы созданы")

    # --- Тесты ---
    test_math, _ = Test.objects.get_or_create(
        test_name='Математика 101',
        author=teacher,
        topic=math_topic,
        defaults={'num_of_questions': 1}
    )
    TestQuestions.objects.get_or_create(test=test_math, question=q1)

    test_physics, _ = Test.objects.get_or_create(
        test_name='Физика 101',
        author=teacher,
        topic=physics_topic,
        defaults={'num_of_questions': 1}
    )
    TestQuestions.objects.get_or_create(test=test_physics, question=q2)

    print("Тесты созданы")
    print("=== Заполнение БД завершено ===")
# Установи django-extensions, если ещё нет:
#
# pip install django-extensions
#
#
# В settings.py добавь:
#
# INSTALLED_APPS += ['django_extensions']
#
#
# Запусти скрипт:
#
# python manage.py runscript populate_db