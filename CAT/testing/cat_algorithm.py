import math
from scipy.optimize import minimize
import numpy as np


class CATAlgorithm3PL:
    def __init__(self, precision_threshold=0.05, max_questions=15):
        self.precision_threshold = precision_threshold
        self.max_questions = max_questions

    def log(self, message):
        """Унифицированный вывод логов"""
        print(f"[CAT-LOG] {message}")

    def probability_3pl(self, theta, a, b, c):
        """Трехпараметрическая логистическая модель"""
        try:
            exponent = -a * (theta - b)
            return float(c + (1 - c) / (1 + math.exp(exponent)))
        except:
            return 0.5

    def log_likelihood(self, theta, responses, questions):
        """Логарифмическая функция правдоподобия"""
        log_lik = 0.0
        for response, question in zip(responses, questions):
            # decimal в float
            a = float(question.discrimination) if question.discrimination else 1.0
            b = float(question.difficulty) if question.difficulty else 0.0
            c = float(question.guessing) if question.guessing else 0.25

            p = self.probability_3pl(theta, a, b, c)

            if response:  # Правильный ответ
                log_lik += math.log(p) if p > 1e-10 else -100
            else:  # Неправильный ответ
                log_lik += math.log(1 - p) if p < 1 - 1e-10 else -100

        return -log_lik  # Минимизируем отрицательное правдоподобие

    def estimate_ability(self, responses, questions, initial_theta=0.0):
        """Оценка уровня знаний theta методом максимального правдоподобия"""
        self.log(f"Оценка способности — вход: θ={initial_theta}, ответов={len(responses)}")

        if not responses:
            return float(initial_theta), 1.0

        try:
            # scipy minimize - функция из библиотеки
            result = minimize(
                self.log_likelihood,
                float(initial_theta),
                args=(responses, questions),
                method='L-BFGS-B',
                bounds=[(-3.0, 3.0)]
            )

            theta_estimate = float(result.x[0])
            se = float(1.0 / math.sqrt(self.fisher_information(theta_estimate, questions)))

            self.log(f"Новая оценка: θ={theta_estimate:.3f}, SE={se:.3f}")

            return theta_estimate, se

        except Exception as e:
            print(f"Error in estimate_ability: {e}")
            self.log(f"Ошибка в estimate_ability: {e}")
            return float(initial_theta), 1.0

    def fisher_information(self, theta, questions):
        """Информация Фишера"""
        information = 0.0
        for question in questions:
            a = float(question.discrimination) if question.discrimination else 1.0
            b = float(question.difficulty) if question.difficulty else 0.0
            c = float(question.guessing) if question.guessing else 0.25

            p = self.probability_3pl(theta, a, b, c)
            information += (a ** 2 * (p - c) ** 2 * (1 - p)) / (p * (1 - c) ** 2)

        return max(information, 0.001)  # Минимальное значение чтобы избежать деления на 0

    def select_next_question(self, theta, available_questions, answered_questions):
        """Выбор следующего вопроса по критерию максимальной информации"""
        self.log(f"Выбор следующего вопроса при θ={theta:.3f}")
        max_info = -1
        best_question = None

        for question in available_questions:
            if question in answered_questions:
                continue

            info = self.fisher_information(theta, [question])

            self.log(
                f"  Вопрос {question.question_id}: "
                f"b={question.difficulty}, a={question.discrimination}, c={question.guessing}, "
                f"info={info:.4f}"
            )

            if info > max_info:
                max_info = info
                best_question = question

        if best_question:
            self.log(f"Выбран вопрос {best_question.question_id} (макс. информативность {max_info:.4f})")
        return best_question

    def should_stop_test(self, se, questions_answered, theta_history=None):
        """Критерий остановки теста"""

        self.log(f"Проверка остановки: SE={se:.3f}, отвечено={questions_answered}")
        MIN_REQUIRED_QUESTIONS = 10

        # максимальное количества вопросов
        if questions_answered >= self.max_questions:
            self.log("⛔ Тест остановлен: достигнут лимит вопросов")
            return True, "max_questions"

        # точность оценки
        if se < self.precision_threshold and questions_answered < MIN_REQUIRED_QUESTIONS:
            self.log("⚠ Достигнута точность, но задан минимум — продолжаем тест")
            return False, "continue"

        if se < self.precision_threshold:
            self.log("⛔ Тест остановлен: достигнута точность")
            return True, "precision"
        # По стабильности оценки theta
        if theta_history and len(theta_history) >= 3:
            recent_thetas = theta_history[-3:]
            theta_change = max(recent_thetas) - min(recent_thetas)
            if theta_change < self.precision_threshold:
                if questions_answered < MIN_REQUIRED_QUESTIONS:
                    self.log("⚠ θ стабилизировалась, но минимум не достигнут — продолжаем")
                    return False, "continue"

                self.log("⛔ Тест остановлен: θ стабилизировалась")
                return True, "stability"

        return False, "continue"