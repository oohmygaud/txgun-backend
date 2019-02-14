# -*- coding: utf-8 -*-

from .defaults import *
import environ

env = environ.Env(DEBUG=(bool, False),) # set default values and casting
DEBUG=os.environ.get('is_zappa', '') != 'true'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'django_s3_storage',
    'rest_framework',
    'auditlog',

    'django_extensions',
    'apps.networks',
    'apps.subscriptions',
    'apps.errors',
    'apps.contracts'

]

DATABASES = {
    'default': env.db('DATABASE_URL', default='psql://tritium:tritium@psql/tritium'),
}

LOGGING['loggers']['scanner'] = {
    'handlers': ['console'],
    'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
}
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(SITE_ROOT + '/templates'),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

ALLOWED_HOSTS = ['txgun.io', '127.0.0.1', 'localhost', '*']

if not DEBUG:
    AWS_REGION = "us-east-2"
    #AWS_ACCESS_KEY_ID = 'AKIAIACHQX4RGS2BAYAQ'
    #AWS_SECRET_ACCESS_KEY = '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'

    AWS_S3_BUCKET_NAME_STATIC = 'zappa-txgun-tritium-static'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_S3_BUCKET_NAME_STATIC
    STATIC_URL = "https://%s/"%AWS_S3_CUSTOM_DOMAIN
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"


    EMAIL_BACKEND = 'django_ses.SESBackend'

    # Additionally, if you are not using the default AWS region of us-east-1,
    # you need to specify a region, like so:
    AWS_SES_REGION_NAME = 'us-east-1'
    AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
