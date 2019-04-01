cp compose/django/requirements.txt Pipfile
pyenv/bin/pip install -r Pipfile

zappa update
pyenv/bin/python manage.py collectstatic --noinput
