from django import forms
from django.utils import timezone
from .models import Users, UserRole

from django import forms
from django.utils import timezone
from .models import Users, UserRole


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label='Пароль'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        }),
        label='Подтверждение пароля'
    )

    role = forms.ChoiceField(
        choices=[('student', 'Студент'), ('teacher', 'Преподаватель')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_role_name'
        }),
        label='Роль'
    )

    group_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер группы (только для студентов)'
        }),
        label='Номер группы'
    )

    class Meta:
        model = Users
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        role_name = cleaned_data.get('role')
        group_number = cleaned_data.get('group_number')

        if password != confirm_password:
            self.add_error('confirm_password', 'Пароли не совпадают.')

        if role_name == 'student' and not group_number:
            self.add_error('group_number', 'Для студентов необходимо указать номер группы.')

        if Users.objects.filter(username=cleaned_data.get('username')).exists():
            self.add_error('username', 'Такое имя пользователя уже занято.')

        if Users.objects.filter(email=cleaned_data.get('email')).exists():
            self.add_error('email', 'Такой email уже зарегистрирован.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        role_name = self.cleaned_data['role']
        group_number = self.cleaned_data.get('group_number')

        role, _ = UserRole.objects.get_or_create(
            role_name='Студент' if role_name == 'student' else 'Преподаватель'
        )

        user.set_password(password)
        user.role = role
        user.num_group = group_number if role_name == 'student' else None
        user.registration_date = timezone.now()

        if commit:
            user.save()

        return user

