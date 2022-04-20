# Models

The database models used in GewässerCampus can be differentiated into
two categories: [](core) and [](auth). The first includes functionality
that is fundamental to GewässerCampus such as the
{class}`gcampus.core.models.Measurement` and
{class}`gcampus.core.models.Water` model. The later contains all models
that are required for authentication.

```{toctree}
:caption: Contents
auth
core
```

## Common Models and Utilities

```{eval-rst}
.. autoclass:: gcampus.core.models.util.DateModelMixin
    :show-inheritance:
    :members: created_at, updated_at
```
