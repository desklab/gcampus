from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


TOKEN_EDIT_PERMISSION_ERROR = _("Token is not allowed to edit this measurement!")
TOKEN_CREATE_PERMISSION_ERROR = _("Token is not allowed to create a measurement!")
TOKEN_EMPTY_ERROR = _("No token has been provided to create or edit a measurement!")
TOKEN_INVALID_ERROR = _("Provided token is not invalid or does not exist.")
