from django import forms

from gcampus.core.models import StudentToken
from gcampus.core.models.token import TeacherToken

from django.utils.translation import gettext_lazy as _

from django.core.exceptions import PermissionDenied


class StudentTokenForm(forms.Form):
    token = forms.CharField(label=_('Student Token'), max_length=8, required=True, min_length=8)
    fields = ["token"]

    def is_valid(self):
        if not super(StudentTokenForm, self).is_valid():
            return False
        if StudentToken.objects.filter(token=self.data["token"]).exists():
            return True
        else:
            return False

class TeacherTokenForm(forms.Form):
    token = forms.CharField(label=_('Teacher Token'), max_length=12, required=True, min_length=12)
    fields = ["token"]

    def is_valid(self):
        if not super(TeacherTokenForm, self).is_valid():
            raise PermissionDenied(_("Token does not exist"))
        if TeacherToken.objects.filter(token=self.data["token"]).exists():
            return True
        else:
            return False

