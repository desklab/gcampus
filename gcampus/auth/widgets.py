from django.forms import HiddenInput


class HiddenTokenInput(HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        """Render Hidden Token Input

        The hidden token input need access to the current session and
        thus it needs access to the request instance. However, this will
        not be available for a widget. The actual widget with the
        correct value will be provided by the ``{% auth_token %}``
        template tag which is used similar to the ``csrf_token``. For
        more information on how to use the token field, see the example
        below.

        Because the value of the token can not be provided from within
        this widget class, nothing will be returned

        .. code-block:: html+django

            {% load auth_token %}
            ...
            <form>
                {% csrf_token %}
                {% auth_token %}
                {{ form }}
            <\form>

        :returns: Empty string as this widget can not be used to provide
            the token value.
        """
        return ""
