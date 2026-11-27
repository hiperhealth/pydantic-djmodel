"""Django settings for the test app."""

from pathlib import Path

SECRET_KEY = 'test-only'  # nosec B105
INSTALLED_APPS = ['tests']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path('test.sqlite3'),
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
MIGRATION_MODULES = {'tests': 'migrations'}
