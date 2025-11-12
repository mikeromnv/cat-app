// add_answers.js

document.addEventListener('DOMContentLoaded', function () {
    const addAnswerBtn = document.getElementById('addAnswerBtn');
    const answersContainer = document.getElementById('answers-container');

    if (!addAnswerBtn || !answersContainer) return;

    // Добавление нового варианта ответа
    addAnswerBtn.addEventListener('click', function () {
        const index = answersContainer.querySelectorAll('.answer-row').length;

        const newAnswer = document.createElement('div');
        newAnswer.classList.add('input-group', 'mb-2', 'answer-row');

        newAnswer.innerHTML = `
            <div class="input-group-text">
                <input type="radio" name="correct_answer" value="${index}" required>
            </div>
            <input type="text" name="answer_text[]" class="form-control" placeholder="Введите вариант ответа" required>
            <button type="button" class="btn btn-outline-danger btn-sm ms-2 remove-answer-btn">✕</button>
        `;

        answersContainer.appendChild(newAnswer);
    });

    // Удаление варианта ответа
    answersContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-answer-btn')) {
            const row = e.target.closest('.answer-row');
            if (row) {
                row.remove();
                // После удаления — обновим value у радио-кнопок (чтобы индексы совпадали)
                const radios = answersContainer.querySelectorAll('input[type="radio"][name="correct_answer"]');
                radios.forEach((radio, i) => {
                    radio.value = i;
                });
            }
        }
    });
});
