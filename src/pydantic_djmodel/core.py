"""Build Django ORM models from Pydantic schemas."""

import re

from copy import deepcopy
from functools import partial
from types import UnionType
from typing import Any, Union, get_args, get_origin

from django.db import models
from pydantic import BaseModel
from pydantic.fields import FieldInfo


def camel_to_snake(name: str) -> str:
    """Convert a camelCase or PascalCase name to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _django_field(name: str, field_info: FieldInfo) -> models.Field:
    annotation: object = field_info.annotation
    nullable = annotation is Any or annotation is type(None)
    if get_origin(annotation) in (Union, UnionType):
        members = get_args(annotation)
        nullable = type(None) in members or Any in members
        non_null = tuple(
            member for member in members if member is not type(None)
        )
        if len(non_null) == 1:
            annotation = non_null[0]

    options: dict[str, Any] = {'null': nullable, 'blank': nullable}
    if field_info.default_factory is not None:
        if field_info.default_factory_takes_validated_data:
            raise ValueError(
                f'{name!r} has a default factory that requires validated data'
            )
        options['default'] = field_info.default_factory
    elif not field_info.is_required():
        default = field_info.default
        if isinstance(default, (dict, list)):
            default = partial(deepcopy, default)
        options['default'] = default

    if annotation is str:
        return models.CharField(max_length=255, **options)
    if annotation is int:
        return models.IntegerField(**options)
    if annotation is float:
        return models.FloatField(**options)
    if annotation is bool:
        return models.BooleanField(**options)
    return models.JSONField(**options)


def pydantic_to_django(
    pydantic_model: type[BaseModel] | BaseModel,
    model_name: str,
    module_name: str | None = None,
    *,
    app_label: str | None = None,
) -> type[models.Model]:
    """
    Build a Django model class from a Pydantic schema.

    Call once at module scope in the consuming app's models module so Django
    discovers the class during app loading.

    Parameters
    ----------
    pydantic_model : type[BaseModel] or BaseModel
        The Pydantic schema class or an instance of that class.
    model_name : str
        The name of the generated Django model class.
    module_name : str, optional
        The consuming model module, usually passed as ``__name__``.
        Django infers the app from this module unless an app label is given.
    app_label : str, optional
        The Django app label to use instead of inferring it from the module.

    Returns
    -------
    type[models.Model]
        The generated Django model class.

    Raises
    ------
    ValueError
        If neither the module nor the app label is given, two fields map to
        the same name, a field uses a reserved primary-key name, or a default
        factory requires validated data.
    """
    if not module_name and not app_label:
        raise ValueError('Pass the Django module_name or app_label')

    attrs: dict[str, Any] = {'__module__': module_name or __name__}
    if app_label:
        attrs['Meta'] = type('Meta', (), {'app_label': app_label})

    schema = (
        type(pydantic_model)
        if isinstance(pydantic_model, BaseModel)
        else pydantic_model
    )
    for name, field_info in schema.model_fields.items():
        field_name = camel_to_snake(name)
        if field_name in {'id', 'pk'}:
            raise ValueError(f'{name!r} maps to reserved field {field_name!r}')
        if field_name in attrs:
            raise ValueError(f'Multiple fields map to {field_name!r}')
        attrs[field_name] = _django_field(name, field_info)

    return type(model_name, (models.Model,), attrs)
