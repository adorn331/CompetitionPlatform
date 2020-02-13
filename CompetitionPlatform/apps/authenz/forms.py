from django import forms


# 用户登录表单
class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '用户名', 'autofocus': ''}))
    password = forms.CharField(label="密码", max_length=30, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '用户密码'}
    ))