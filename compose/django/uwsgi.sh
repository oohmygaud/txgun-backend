#!/usr/bin/env bash

export SERVICE=uwsgi
export METRIC_ACCESS_KEY_ID=AKIARNKH4B5PSANBJSHL
export METRIC_SECRET_ACCESS_KEY=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

uwsgi --chdir=/app \
    --http 0.0.0.0:8000 \
    --module=wsgi:application \
    --env DJANGO_SETTINGS_MODULE=conf \
    --master --pidfile=/tmp/project-master.pid \
    --socket=127.0.0.1:49152 \
    --processes=5 \
    --uid=1000 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum