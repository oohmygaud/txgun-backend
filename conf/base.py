# -*- coding: utf-8 -*-

from .defaults import *
from datetime import timedelta
import environ

env = environ.Env(DEBUG=(bool, False),) # set default values and casting
DEBUG=os.environ.get('is_zappa', '') != 'true'

INSTALLED_APPS = [
    'django.contrib.auth',
    'jet.dashboard',
    'jet',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',

    'django_s3_storage',
    'rest_framework',
    'rest_registration',
    'auditlog',

    'django_filters',
    'django_extensions',


    'apps.networks',
    'apps.subscriptions',
    'apps.errors',
    'apps.contracts',
    'apps.users'

]

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_URL': 'https://txgun.io/verify-user/',
    'RESET_PASSWORD_VERIFICATION_URL': 'https://txgun.io/reset-password/',
    'REGISTER_EMAIL_VERIFICATION_URL': 'https://txgun.io/verify-email/',

    'VERIFICATION_FROM_EMAIL': 'noreply@txgun.io',
}

AUTH_USER_MODEL = 'users.CustomUser'

DATABASES = {
    'default': env.db('DATABASE_URL', default='psql://tritium:tritium@psql/tritium'),
}

LOGGING['loggers']['scanner'] = {
    'handlers': ['console'],
    'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
}

LOGGING['loggers']['subscriptions'] = {
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
        'APP_DIRS': True,
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            # ],
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

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',)
}

AWS_S3_BUCKET_NAME_STATIC = 'zappa-txgun-tritium-static'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_S3_BUCKET_NAME_STATIC

if not DEBUG:
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
    AWS_REGION = "us-east-2"
    #AWS_ACCESS_KEY_ID = 'AKIAIACHQX4RGS2BAYAQ'
    #AWS_SECRET_ACCESS_KEY = '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'

    STATIC_URL = "https://%s/"%AWS_S3_CUSTOM_DOMAIN

    EMAIL_BACKEND = 'django_ses.SESBackend'

    # Additionally, if you are not using the default AWS region of us-east-1,
    # you need to specify a region, like so:
    AWS_SES_REGION_NAME = 'us-east-1'
    AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'

# EMAIL_BACKEND='conf.test_settings.MockEmailBackend'

SIGNUP_BONUS_CREDITS = 1000
NOTIFICATION_CREDIT_COST = 1

APPEND_SLASH=True


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
