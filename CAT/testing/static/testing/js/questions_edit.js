document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-btn");
    const addQuestionForm = document.querySelector("#addQuestionForm");
    const editQuestionForm = document.querySelector("#editQuestionForm");
    const addAnswerBtn = document.querySelector("#addAnswerBtn");
    const editAddAnswerBtn = document.querySelector("#editAddAnswerBtn");

    // Обработка добавления новых вариантов ответов
    addAnswerBtn.addEventListener("click", addAnswerRow);
    editAddAnswerBtn.addEventListener("click", addEditAnswerRow);

    // Функция для добавления нового варианта ответа
    function addAnswerRow(container = null) {
        const targetContainer = container || document.querySelector("#answers-container");
        const answerCount = targetContainer.querySelectorAll('.answer-row').length;

        const answerRow = document.createElement("div");
        answerRow.className = "input-group mb-2 answer-row";
        answerRow.innerHTML = `
            <div class="input-group-text">
                <input type="radio" name="correct_answer" value="${answerCount}" required>
            </div>
            <input type="text" name="answer_text[]" class="form-control" placeholder="Введите вариант ответа" required>
            <button type="button" class="btn btn-outline-danger btn-sm ms-2 remove-answer-btn">✕</button>
        `;
        targetContainer.appendChild(answerRow);

        // Добавляем обработчик для кнопки удаления
        answerRow.querySelector('.remove-answer-btn').addEventListener('click', function() {
            this.closest('.answer-row').remove();
            updateRadioValues(targetContainer);
        });
    }

    // Функция для обновления значений radio кнопок
    function updateRadioValues(container) {
        const rows = container.querySelectorAll('.answer-row');
        rows.forEach((row, index) => {
            const radio = row.querySelector('input[type="radio"]');
            radio.value = index;
        });
    }

    // Функция для добавления ответов в модалку редактирования
    function addEditAnswerRow() {
        addAnswerRow(document.querySelector("#edit-answers-container"));
    }

    // Обработка кнопок редактирования
    editButtons.forEach(button => {
        button.addEventListener("click", function () {
            const questionId = this.dataset.id;
            loadQuestionForEdit(questionId);
        });
    });

    // Загрузка данных вопроса для редактирования
    function loadQuestionForEdit(questionId) {
        fetch(`/get_question/${questionId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка загрузки вопроса');
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    showNotification(data.error || "Ошибка загрузки вопроса", 'error');
                    return;
                }

                // Заполняем скрытое поле с ID вопроса
                document.querySelector("#editQuestionId").value = data.question.question_id;

                // Заполняем основные поля
                document.querySelector("#editQuestionForm input[name='text_question']").value = data.question.text_question;
                document.querySelector("#editQuestionForm select[name='topic']").value = data.question.topic_id || '';
                document.querySelector("#editQuestionForm input[name='difficulty']").value = data.question.difficulty || '';
                document.querySelector("#editQuestionForm input[name='discrimination']").value = data.question.discrimination || '';
                document.querySelector("#editQuestionForm input[name='guessing']").value = data.question.guessing || '';

                // Очищаем и заполняем контейнер с ответами
                const answersContainer = document.querySelector("#edit-answers-container");
                answersContainer.innerHTML = "";

                data.answers.forEach((answer, index) => {
                    const answerRow = document.createElement("div");
                    answerRow.className = "input-group mb-2 answer-row";
                    answerRow.innerHTML = `
                        <div class="input-group-text">
                            <input type="radio" name="correct_answer" value="${index}" ${answer.is_correct ? "checked" : ""}>
                        </div>
                        <input type="text" name="answer_text[]" class="form-control" value="${answer.answer_text}" required>
                        <button type="button" class="btn btn-outline-danger btn-sm ms-2 remove-answer-btn">✕</button>
                    `;
                    answersContainer.appendChild(answerRow);

                    // Добавляем обработчик для кнопки удаления
                    answerRow.querySelector('.remove-answer-btn').addEventListener('click', function() {
                        this.closest('.answer-row').remove();
                        updateRadioValues(answersContainer);
                    });
                });

                // Показываем модальное окно редактирования
                const modal = new bootstrap.Modal(document.getElementById("editQuestionModal"));
                modal.show();
            })
            .catch(err => {
                console.error("Ошибка загрузки вопроса:", err);
                showNotification('Ошибка загрузки вопроса', 'error');
            });
    }

    // Обработка отправки формы редактирования
    editQuestionForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const questionId = document.querySelector("#editQuestionId").value;
        const formData = new FormData(this);

        fetch(`/update_question/${questionId}/`, {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('#editQuestionForm input[name="csrfmiddlewaretoken"]').value,
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('editQuestionModal'));
                modal.hide();

                // Показываем уведомление об успехе
                showNotification(data.message, 'success');

                // Обновляем таблицу через 1 секунду
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification(data.message || 'Ошибка при обновлении вопроса', 'error');
            }
        })
        .catch(err => {
            console.error("Ошибка:", err);
            showNotification('Произошла ошибка при сохранении', 'error');
        });
    });

    // Функция для показа уведомлений
    function showNotification(message, type) {
        // Удаляем старые уведомления
        const oldAlerts = document.querySelectorAll('.custom-alert');
        oldAlerts.forEach(alert => alert.remove());

        // Создаем новое уведомление
        const alert = document.createElement('div');
        alert.className = `custom-alert alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alert.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Автоматически скрываем через 3 секунды
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 3000);
    }

    // Добавляем обработчики для кнопок удаления в основной форме
    document.querySelectorAll(".remove-answer-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            this.closest('.answer-row').remove();
            updateRadioValues(document.querySelector("#answers-container"));
        });
    });
});