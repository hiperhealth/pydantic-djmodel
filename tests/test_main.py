"""Tests for model generation and downstream Django integration."""

import os
import subprocess
import sys

from pathlib import Path

import pytest

from django.apps import apps
from django.db import models
from pydantic import BaseModel, Field
from pydantic_djmodel.core import pydantic_to_django

from tests.models import Record, RecordSchema


def test_import_has_no_django_side_effects(tmp_path: Path) -> None:
    """Import the converter before configuring Django."""
    env = os.environ.copy()
    env.pop('DJANGO_SETTINGS_MODULE', None)
    subprocess.run(
        [
            sys.executable,
            '-c',
            'import sys; from django.conf import settings; '
            'path = sys.path.copy(); import pydantic_djmodel.core; '
            'assert sys.path == path; assert not settings.configured',
        ],
        cwd=tmp_path,
        env=env,
        check=True,
    )


def test_model_fields_and_defaults() -> None:
    """Map supported annotations and preserve common defaults."""
    assert apps.get_model('tests', 'Record') is Record
    fields = Record._meta
    assert isinstance(fields.get_field('display_name'), models.CharField)
    assert fields.get_field('display_name').max_length == 255
    assert isinstance(fields.get_field('count'), models.IntegerField)
    assert not fields.get_field('count').null
    assert isinstance(fields.get_field('score'), models.FloatField)
    assert fields.get_field('score').null
    assert isinstance(fields.get_field('reference'), models.IntegerField)
    assert fields.get_field('reference').null
    assert isinstance(fields.get_field('active'), models.BooleanField)
    assert not fields.get_field('show').has_default()
    assert isinstance(fields.get_field('tags'), models.JSONField)
    assert isinstance(fields.get_field('variant'), models.JSONField)
    assert fields.get_field('optional_variant').null

    record = Record()
    assert record.active is True
    assert record.score is None
    record.tags.append('example')
    record.payload['state'] = 'updated'
    assert Record().tags == []
    assert Record().payload == {'state': 'new'}


def test_explicit_app_label() -> None:
    """Register a schema instance with the app when no module is given."""
    schema = RecordSchema(displayName='Demo', count=1, show=False, variant=1)
    generated = pydantic_to_django(schema, 'ExplicitLabel', app_label='tests')
    assert apps.get_model('tests', 'ExplicitLabel') is generated


def test_requires_module_or_app_label() -> None:
    """Explain which Django app information is missing."""
    with pytest.raises(ValueError, match='module_name or app_label'):
        pydantic_to_django(RecordSchema, 'NoApp')


def test_rejects_name_collisions() -> None:
    """Avoid replacing a field when normalized names collide."""

    class ConflictingSchema(BaseModel):
        displayName: str
        display_name: str

    with pytest.raises(ValueError, match='Multiple fields'):
        pydantic_to_django(ConflictingSchema, 'Conflict', __name__)


def test_rejects_reserved_field_name() -> None:
    """Preserve Django's implicit primary key."""

    class ReservedSchema(BaseModel):
        id: str

    with pytest.raises(ValueError, match='reserved field'):
        pydantic_to_django(ReservedSchema, 'Reserved', __name__)


def test_rejects_defaults_that_need_pydantic_validation() -> None:
    """Reject a factory Django cannot call with zero arguments."""

    class DependentDefault(BaseModel):
        name: str
        label: str = Field(default_factory=lambda data: data['name'])

    with pytest.raises(ValueError, match='requires validated data'):
        pydantic_to_django(DependentDefault, 'Dependent', __name__)


def test_generated_model_migrates_and_saves(tmp_path: Path) -> None:
    """Discover, migrate, and use a model in a fresh Django process."""
    migrations = tmp_path / 'migrations'
    migrations.mkdir()
    (migrations / '__init__.py').touch()
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    root = str(Path(__file__).resolve().parents[1])
    paths = [root, env['PYTHONPATH']] if env.get('PYTHONPATH') else [root]
    env['PYTHONPATH'] = os.pathsep.join(paths)

    script = """
import django
django.setup()
from django.apps import apps
from django.core.management import call_command

call_command('check')
call_command('makemigrations', 'tests', verbosity=0)
call_command('migrate', verbosity=0)
call_command('makemigrations', 'tests', check=True, dry_run=True, verbosity=0)

Record = apps.get_model('tests', 'Record')
first = Record.objects.create(
    display_name='First', count=2, show=True, variant='string', tags=['saved']
)
second = Record.objects.create(
    display_name='Second', count=1, show=False, variant=4
)
first.refresh_from_db()
second.refresh_from_db()
assert first.tags == ['saved']
assert first.variant == 'string'
assert second.variant == 4
assert second.tags == []
assert second.payload == {'state': 'new'}
assert second.score is None
assert second.show is False
assert second.active is True
"""
    subprocess.run(
        [sys.executable, '-c', script], cwd=tmp_path, env=env, check=True
    )
    assert (migrations / '0001_initial.py').is_file()
