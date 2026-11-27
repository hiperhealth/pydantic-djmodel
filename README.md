# pydantic-djmodel

Generate a Django ORM model from a Pydantic v2 schema. Use the generated model
in an installed Django app and manage its tables with standard Django migrations.

## Install

```bash
python -m pip install "pydantic-djmodel>=0.2.0"
```

## Generate a model

In the `models.py` of an app listed in `INSTALLED_APPS`:

```python
from pydantic import BaseModel, Field
from pydantic_djmodel.core import pydantic_to_django


class RecordSchema(BaseModel):
    title: str
    score: float | None = None
    tags: list[str] = Field(default_factory=list)


Record = pydantic_to_django(RecordSchema, "Record", __name__)
```

Run `python manage.py makemigrations` and `python manage.py migrate`.
Then save data with the Django ORM:

```python
from records.models import Record, RecordSchema  # Replace records with your app.

data = RecordSchema(title="First record", tags=["example"])
record = Record.objects.create(**data.model_dump(mode="json"))
```

See [the installation and usage guide](https://github.com/hiperhealth/pydantic-djmodel/blob/main/docs/installation.md)
for field mappings, defaults, and upgrading from 0.1.0.

## License

MIT. Created with [SciCookie](https://github.com/osl-incubator/scicookie).
