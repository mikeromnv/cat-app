from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone




class Topic(models.Model):
    topic_id = models.AutoField(primary_key=True)
    topic_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.topic_name

    class Meta:
        db_table = 'topic'


class Questions(models.Model):
    question_id = models.AutoField(primary_key=True)
    text_question = models.TextField()
    difficulty = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    discrimination = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    guessing = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    correct_answer = models.ForeignKey('Answers', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Question {self.question_id}: {self.text_question[:50]}"

    class Meta:
        db_table = 'questions'

class Answers(models.Model):
    answer_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer_number = models.IntegerField()
    answer_text = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Answer {self.answer_number} for Question {self.question.question_id}"

    class Meta:
        db_table = 'answers'

class Test(models.Model):
    test_id = models.AutoField(primary_key=True)
    num_of_questions = models.IntegerField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    test_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.test_name

    class Meta:
        db_table = 'test'

class TestQuestions(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)

    def __str__(self):
        return f"Test {self.test.test_id} - Question {self.question.question_id}"

    class Meta:
        db_table = 'test_questions'
        unique_together = ('test', 'question')

class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100)

    def __str__(self):
        return self.status_name

    class Meta:
        db_table = 'status'

class TestSessions(models.Model):
    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True)
    current_ability_estimate = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    standard_error = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    next_question = models.ForeignKey(Questions, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Session {self.session_id} - User {self.user_id}"

    class Meta:
        db_table = 'test_sessions'

class UserAnswers(models.Model):
    user_answer_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(TestSessions, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey(Questions, on_delete=models.SET_NULL, null=True)
    selected_answer = models.ForeignKey(Answers, on_delete=models.SET_NULL, null=True)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(default=timezone.now)
    order_in_test = models.IntegerField()
    ability_after_answer = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    standard_error_after = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    probability_of_correct = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)

    def __str__(self):
        return f"UserAnswer {self.user_answer_id} - Session {self.session_id}"

    class Meta:
        db_table = 'user_answers'