function toggleGroupField() {
    const roleSelect = document.getElementById('id_role_name');
    const groupField = document.getElementById('groupField');
    const groupInput = document.getElementById('id_group_number');

    if (roleSelect && roleSelect.value === 'student') {
        groupField.style.display = 'block';
        if (groupInput) groupInput.required = true;
    } else {
        if (groupField) groupField.style.display = 'none';
        if (groupInput) {
            groupInput.required = false;
            groupInput.value = ''; // очищаем поле при смене роли
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    toggleGroupField();

    const roleSelect = document.getElementById('id_role_name');
    if (roleSelect) {
        roleSelect.addEventListener('change', toggleGroupField);
    }
});
