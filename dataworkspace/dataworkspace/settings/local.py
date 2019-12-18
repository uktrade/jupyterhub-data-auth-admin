from dataworkspace.settings.base import *  # noqa: F403, F401
from dataworkspace.settings.base import env

DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    **{
        database_name: {
            'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
            'CONN_MAX_AGE': 0,
            **database,
            'OPTIONS': {'sslmode': 'require', 'MAX_CONNS': 100},
        }
        for database_name, database in env['DATA_DB'].items()
    },
}

STATIC_URL = '/static/'
