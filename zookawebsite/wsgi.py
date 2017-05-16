"""
This is the WSGI script needed by web servers to serve this Django app.
This should be all that's needed to launch this Django app through web
servers like Apache.

To learn more about this script, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/ and
http://wsgi.readthedocs.org/en/latest/
"""
import os

from django.core.wsgi import get_wsgi_application

# For the WSGI script, always set the 'DJANGO_SETTINGS_MODULE' environment
# variable to the settings module for this Django app.
os.environ['DJANGO_SETTINGS_MODULE'] = 'zookawebsite.settings'

#: The 'application' object implemented with Django's
#: :meth:`django.core.wsgi.get_wsgi_application` method.
application = get_wsgi_application()
