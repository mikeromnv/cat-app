let page = 1;
const loadMoreBtn = document.getElementById('loadMoreBtn');
const container = document.getElementById('questions-container');

loadMoreBtn.addEventListener('click', () => {
    page++;
    fetch(`/questions/?page=${page}`)
        .then(res => res.text())
        .then(html => {
            const parser = new DOMParser();
            const newQuestions = parser.parseFromString(html, 'text/html')
                .querySelector('#questions-container').innerHTML;

            container.insertAdjacentHTML('beforeend', newQuestions);

            // Если новых вопросов нет — скрываем кнопку
            if (!newQuestions.trim()) {
                loadMoreBtn.style.display = 'none';
            }
        })
        .catch(err => console.error('Ошибка загрузки:', err));
});
