from django import forms
from django.core import validators


class statuses(forms.Form):
    status = forms.CharField(label="", widget=forms.TextInput(attrs={'class': "form-control", 'id': "searchbox", 'name': "statuses", 'placeholder': "ex : 404, 403"}))


class search_box(forms.Form):
    search = forms.CharField(label="", widget=forms.TextInput(attrs={'class': "form-control", 'name': "search", 'placeholder': "Search for URL"}))
