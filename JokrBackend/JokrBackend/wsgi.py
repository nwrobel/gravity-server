"""
WSGI config for JokrBackend project.

It exposes the WSGI callable as a module-level variable named ``application``.
"
For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
#===============================================================================
# WSGI Config file
#===============================================================================

import os
import site
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JokrBackend.Settings.DevEnvSettings')

application = get_wsgi_application()
