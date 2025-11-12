// questions_delete.js

document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("questions-container");

    if (!container) return;

    container.addEventListener("click", async function (e) {
        const btn = e.target.closest(".delete-btn");
        if (!btn) return;

        const questionId = btn.getAttribute("data-id");
        if (!questionId) return;

        if (!confirm("Вы уверены, что хотите удалить этот вопрос?")) return;

        try {
            const response = await fetch(`/delete_question/${questionId}/`, {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (data.success) {
                // Удаляем карточку вопроса из DOM
                btn.closest(".col-md-6, .col-lg-4").remove();
            } else {
                alert(data.error || "Ошибка при удалении вопроса.");
            }
        } catch (error) {
            console.error("Ошибка при удалении:", error);
            alert("Произошла ошибка. Попробуйте позже.");
        }
    });

    // Получаем CSRF-токен из cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
