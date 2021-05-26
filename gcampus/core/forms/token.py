from django import forms


class StudentTokenForm(forms.Form):
    token = forms.CharField(label='StudentToken', max_length=8, required=True, min_length=8)
    fields = ["token"]


class TeacherTokenForm(forms.Form):
    token = forms.CharField(label='Teacher Token', max_length=12, required=True, min_length=12)
    fields = ["token"]
