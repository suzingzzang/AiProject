import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.core.exceptions import ValidationError

from .models import CustomUser

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"autofocus": True}),
        error_messages={"required": "이메일을 입력해주세요.", "invalid": "올바른 이메일을 입력해주세요."},
    )
    phonenumber = forms.CharField(
        label="Phone Number",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "전화번호를 입력해주세요."}),
        error_messages={"required": "전화번호를 입력해주세요.", "invalid": "올바른 전화번호를 입력해주세요."},
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={"required": "비밀번호를 입력해주세요."},
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={"required": ""},
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "phonenumber")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        print(email)
        if email:
            regex = r"^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            if not re.match(regex, email):
                raise ValidationError("올바른 이메일을 입력해주세요.")
        return email

    def clean_phonenumber(self):
        phonenumber = self.cleaned_data.get("phonenumber")
        print(phonenumber)
        if phonenumber:
            regex = r"^\d{3}-\d{4}-\d{4}$"
            if not re.match(regex, phonenumber):
                raise ValidationError("올바른 형식: 000-0000-0000")
        else:
            raise ValidationError("전화번호를 입력해주세요.")
        return phonenumber

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("비밀번호가 일치하지 않습니다.")
            if len(password2) < 8:
                raise ValidationError("비밀번호는 8자 이상이어야 합니다.")
        if not password1:
            raise ValidationError("")
        return password2


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(label="Email", widget=forms.TextInput(attrs={"autofocus": True}), error_messages={"required": "이메일을 입력해주세요."})
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        error_messages={"required": "비밀번호를 입력해주세요."},
    )

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Regular expression for validating an Email
            regex = r"^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            if not re.match(regex, username):
                raise ValidationError("올바른 이메일를 입력해주세요.")
        return username

    def clean_password(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            try:
                user = User.objects.get(email=username)
                # User exists, now authenticate to check the password
                if not user.check_password(password):
                    raise ValidationError("비밀번호가 올바르지 않습니다.")
            except User.DoesNotExist:
                raise ValidationError("존재하지 않는 계정입니다.")
        return password
