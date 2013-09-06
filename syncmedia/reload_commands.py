# -*- coding: utf-8 -*-

from django.conf import settings

# GUNICORN_WSGI="""ps --ppid $(cat /var/run/gunicorn/%s.wsgi.pid) | grep python | tr -d " " | cut -d "?" -f1 | xargs -I{} kill -HUP {}""" % settings.PROJECT_NAME

GUNICORN_WSGI="""ps -o pid --ppid $(cat /var/run/gunicorn/%s.wsgi.pid) --noheaders | xargs -I{} kill -HUP {}""" % settings.PROJECT_NAME