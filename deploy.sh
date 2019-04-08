cp compose/django/requirements.txt Pipfile
pyenv/bin/pip install -r Pipfile

pyenv/bin/python manage.py collectstatic --noinput

zappa update

zappa manage production migrate
