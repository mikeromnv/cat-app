from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from testing.models import Topic, Questions, Answers, Test, TestQuestions
from django.utils import timezone


class Command(BaseCommand):
    help = 'Создает тестовые данные для теста по Django'

    def handle(self, *args, **options):
        User = get_user_model()

        # Получаем первого преподавателя (или создаем если нет)
        try:
            teacher = User.objects.filter(role__role_name='Преподаватель').first()
            if not teacher:
                teacher = User.objects.first()
        except:
            teacher = User.objects.first()

        if not teacher:
            self.stdout.write(self.style.ERROR('Нет пользователей в системе! Сначала создайте пользователя.'))
            return

        # Создаем тему "Веб-разработка на Django"
        topic, created = Topic.objects.get_or_create(
            topic_name='Веб-разработка на Django',
            defaults={
                'description': 'Фреймворк Django для создания веб-приложений на Python'
            }
        )

        # Создаем вопросы с параметрами IRT (сложность, дискриминативность, угадывание)
        questions_data = [
            # Легкие вопросы (difficulty: -2.0 до 0.0)
            {
                'text': 'Что такое Django?',
                'difficulty': -1.8,
                'discrimination': 0.9,
                'guessing': 0.15,
                'answers': [
                    ('Язык программирования', False),
                    ('Веб-фреймворк для Python', True),
                    ('База данных', False),
                    ('Операционная система', False)
                ]
            },
            {
                'text': 'Какой файл содержит настройки проекта Django?',
                'difficulty': -1.5,
                'discrimination': 1.1,
                'guessing': 0.20,
                'answers': [
                    ('models.py', False),
                    ('views.py', False),
                    ('settings.py', True),
                    ('urls.py', False)
                ]
            },
            {
                'text': 'Для чего используется команда "python manage.py runserver"?',
                'difficulty': -1.2,
                'discrimination': 1.0,
                'guessing': 0.10,
                'answers': [
                    ('Для создания миграций', False),
                    ('Для запуска сервера разработки', True),
                    ('Для установки пакетов', False),
                    ('Для тестирования приложения', False)
                ]
            },
            {
                'text': 'Что такое ORM в Django?',
                'difficulty': -1.0,
                'discrimination': 1.2,
                'guessing': 0.15,
                'answers': [
                    ('Object-Random Model', False),
                    ('Object-Relational Mapping', True),
                    ('Online-Resource Manager', False),
                    ('Object-Runtime Module', False)
                ]
            },
            {
                'text': 'Как создать приложение в Django?',
                'difficulty': -0.8,
                'discrimination': 0.8,
                'guessing': 0.25,
                'answers': [
                    ('django new app', False),
                    ('python create app', False),
                    ('python manage.py startapp', True),
                    ('django-admin startproject', False)
                ]
            },

            # Вопросы средней сложности (difficulty: 0.0 до 1.0)
            {
                'text': 'Что такое middleware в Django?',
                'difficulty': 0.2,
                'discrimination': 1.3,
                'guessing': 0.08,
                'answers': [
                    ('Промежуточное ПО для обработки запросов/ответов', True),
                    ('База данных', False),
                    ('Шаблонизатор', False),
                    ('Система кэширования', False)
                ]
            },
            {
                'text': 'Как работает механизм миграций в Django?',
                'difficulty': 0.5,
                'discrimination': 1.4,
                'guessing': 0.05,
                'answers': [
                    ('Создает SQL-запросы на основе моделей', True),
                    ('Копирует файлы базы данных', False),
                    ('Генерирует HTML-шаблоны', False),
                    ('Оптимизирует производительность', False)
                ]
            },
            {
                'text': 'Что такое QuerySet в Django?',
                'difficulty': 0.7,
                'discrimination': 1.5,
                'guessing': 0.10,
                'answers': [
                    ('Набор запросов к базе данных', True),
                    ('Тип данных для хранения запросов', False),
                    ('Система валидации форм', False),
                    ('Модуль для работы с API', False)
                ]
            },
            {
                'text': 'Как работает система аутентификации Django?',
                'difficulty': 0.9,
                'discrimination': 1.2,
                'guessing': 0.07,
                'answers': [
                    ('Через модель User и модуль auth', True),
                    ('Только через сторонние библиотеки', False),
                    ('Через cookies и сессии', False),
                    ('Не поддерживает аутентификацию', False)
                ]
            },
            {
                'text': 'Что такое Django REST Framework?',
                'difficulty': 1.0,
                'discrimination': 1.1,
                'guessing': 0.12,
                'answers': [
                    ('Фреймворк для создания REST API', True),
                    ('Система для работы с базами данных', False),
                    ('Модуль для тестирования', False),
                    ('Библиотека для фронтенда', False)
                ]
            },

            # Сложные вопросы (difficulty: 1.0 до 2.0)
            {
                'text': 'Как работает механизм кэширования в Django?',
                'difficulty': 1.3,
                'discrimination': 1.6,
                'guessing': 0.04,
                'answers': [
                    ('Через бэкенды (redis, memcached, database)', True),
                    ('Только в оперативной памяти', False),
                    ('Автоматически для всех запросов', False),
                    ('Только для статических файлов', False)
                ]
            },
            {
                'text': 'Что такое сигналы (signals) в Django и когда их использовать?',
                'difficulty': 1.6,
                'discrimination': 1.4,
                'guessing': 0.03,
                'answers': [
                    ('Механизм для выполнения кода при событиях', True),
                    ('Система оповещений пользователей', False),
                    ('Протокол для работы с WebSocket', False),
                    ('Модуль для обработки ошибок', False)
                ]
            },
            {
                'text': 'Как работает система транзакций в Django?',
                'difficulty': 1.8,
                'discrimination': 1.5,
                'guessing': 0.05,
                'answers': [
                    ('Обеспечивает атомарность операций с БД', True),
                    ('Управляет HTTP-сессиями', False),
                    ('Кэширует результаты запросов', False),
                    ('Валидирует данные форм', False)
                ]
            },
            {
                'text': 'Что такое ContentTypes framework в Django?',
                'difficulty': 2.0,
                'discrimination': 1.3,
                'guessing': 0.02,
                'answers': [
                    ('Система для работы с любыми моделями', True),
                    ('Модуль для генерации контента', False),
                    ('Фреймворк для типизации данных', False),
                    ('Система валидации MIME-типов', False)
                ]
            },
            {
                'text': 'Как работает механизм индексов в Django ORM?',
                'difficulty': 2.2,
                'discrimination': 1.7,
                'guessing': 0.01,
                'answers': [
                    ('Через класс Index в Meta модели', True),
                    ('Автоматически для всех полей', False),
                    ('Только для первичных ключей', False),
                    ('Через отдельный файл конфигурации', False)
                ]
            }
        ]

        self.stdout.write(f'Создаем тест по теме: {topic.topic_name}')

        # Создаем вопросы
        created_questions = []
        for i, q_data in enumerate(questions_data, 1):
            question = Questions.objects.create(
                text_question=q_data['text'],
                difficulty=q_data['difficulty'],
                discrimination=q_data['discrimination'],
                guessing=q_data['guessing'],
                topic=topic,
                author=teacher
            )

            # Создаем варианты ответов
            correct_answer = None
            for j, (answer_text, is_correct) in enumerate(q_data['answers'], 1):
                answer = Answers.objects.create(
                    question=question,
                    answer_number=j,
                    answer_text=answer_text,
                    is_correct=is_correct
                )
                if is_correct:
                    correct_answer = answer

            # Устанавливаем правильный ответ
            if correct_answer:
                question.correct_answer = correct_answer
                question.save()

            created_questions.append(question)
            self.stdout.write(f'  Создан вопрос {i}: {q_data["text"][:50]}...')

        # Создаем тест
        test = Test.objects.create(
            test_name='Django Framework - адаптивное тестирование',
            num_of_questions=len(created_questions),
            author=teacher,
            topic=topic
        )

        # Добавляем все вопросы в тест
        for question in created_questions:
            TestQuestions.objects.create(
                test=test,
                question=question
            )

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Успешно создан тест "{test.test_name}"!\n'
            f'   • Тема: {topic.topic_name}\n'
            f'   • Вопросов: {len(created_questions)}\n'
            f'   • Автор: {teacher.username}\n'
            f'   • ID теста: {test.test_id}'
        ))

        self.stdout.write(self.style.SUCCESS(
            '\n🎯 Теперь студенты могут проходить адаптивное тестирование!\n'
            '   Сложность вопросов варьируется от -2.0 (легкие) до +2.2 (очень сложные)'
        ))