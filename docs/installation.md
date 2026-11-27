# Installation and usage

Use Python 3.10 or later, Pydantic 2.10.6 or later in the 2.x series, and
Django 5.2 or 6.x. Django 6.0 requires Python 3.12 or later.

```bash
python -m pip install "pydantic-djmodel>=0.2.0"
```

To install a specific commit from GitHub, use its commit SHA:

```bash
python -m pip install "pydantic-djmodel @ git+https://github.com/hiperhealth/pydantic-djmodel.git@<commit-sha>"
```

## Add a model to your app

In `records/models.py`, where `records` is listed in your Django project's
`INSTALLED_APPS`:

```python
from pydantic import BaseModel, Field
from pydantic_djmodel.core import pydantic_to_django


class RecordSchema(BaseModel):
    title: str
    score: float | None = None
    tags: list[str] = Field(default_factory=list)


Record = pydantic_to_django(RecordSchema, "Record", __name__)
```

Call the factory once at module scope. Passing `__name__` lets Django infer
the app from the module. For a module outside the app, pass
`app_label="records"` explicitly and make sure your app loads the generated
model during startup.

```bash
python manage.py check
python manage.py makemigrations records
python manage.py migrate
```

In `python manage.py shell`:

```python
from records.models import Record, RecordSchema

data = RecordSchema(title="First record", tags=["example"])
saved = Record.objects.create(**data.model_dump(mode="json"))
assert Record.objects.get(pk=saved.pk).tags == ["example"]
```

## Field mapping

| Pydantic annotation | Django field |
| --- | --- |
| `str` | `CharField(max_length=255)` |
| `int` | `IntegerField` |
| `float` | `FloatField` |
| `bool` | `BooleanField` |
| Collections, nested values, heterogeneous unions, and other types | `JSONField` |

`T | None` and `Optional[T]` use the field for `T` with database nulls
enabled. A heterogeneous union that includes `None` uses a nullable JSON
field. Django receives declared defaults and zero-argument, migration-serializable
factories such as `list` and `dict`. JSON field defaults and factory return
values must be JSON-compatible. Factories that need validated data cannot
be used on a schema passed to the converter.

Field names are converted to snake case. If a field changes names during
conversion, pass its Django name explicitly when calling the ORM.
Django keeps its own primary key. To accept input named `id` or `pk`, use a
separate Pydantic field name such as `external_id` and set a Pydantic alias.

Validate the input with Pydantic and serialize nested values with
`model_dump(mode="json")` before writing JSON fields. Pydantic validators,
constraints, and relationships are outside the generated Django model.
Use regular Django models for fields that require database relationships or
specialized storage.

## Upgrade from 0.1.0

Pass the consuming model module or an app label when generating a model.
Generate and review Django migrations before applying them to existing data.
Fields with annotations that exclude `None` now generate non-nullable
columns. Backfill existing null values before enforcing the new constraints.
