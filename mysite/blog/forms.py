from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post, User, Profile


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "status", "tag"]


# class UserRegistrationForm(forms.ModelForm):
#     password1 = forms.CharField(label='Password',
#                                 widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Password Again',
#                                 widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'email']

#     def clean_password1(self):
#         password1= self.cleaned_data.get('password1')
#         try:
#             validate_password(password1)
#         except forms.ValidationError as error:
#             raise forms.ValidationError(error)

#         return password1
    
#     def clean_password2(self):
#         password2= self.cleaned_data.get('password2')
#         try:
#             validate_password(password2)
#         except forms.ValidationError as error:
#             raise forms.ValidationError(error)

#         return password2



class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Again', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']


    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        validate_password(password1, self.instance)  # Validate the password using Django's built-in password validators
        return password1
    
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match")

        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']

    # def __init__(self, user, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['user'].initial = user
    #     self.fields['user'].widget = forms.HiddenInput()
