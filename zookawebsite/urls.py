"""
This module defines the *urlpatterns* list which sets your URL paths to
support as well as the dispatch methods for them. The Python path to this
module is set in the :data:`ROOT_URLCONF` Django setting.

Here, the dispatch methods defined are simple methods that only need to
take in the :class:`django.http.HttpRequest` object that's always passed in.
More complicated URL handlers can be defined, such as URL that pass in
extra parameters based off of regex match groups in the URL regexes, and
other URLs that have extra hard-coded parameters passed in.
For more information about specifying these advanced URL paths, see
https://docs.djangoproject.com/en/stable/topics/http/urls/ .
"""
import local_pkg_django_setup.utils
from django.conf import settings
from django.conf.urls import url, include
import django.views.static
from django.views.generic import RedirectView, ListView, DetailView
from django.contrib import admin
admin.autodiscover()

def see_source_code():
    """
    Noop method. This is only implemented so that Sphinx's Viewcode
    extension generates the source code page for this module. Click the
    *source* link to see the source code.
    """
    pass


#: The *urlpatterns* list used by Django. See the source code for info about
#: all url patterns implemented.
urlpatterns = [
    # The '/ping' and '/sping' path handlers used by the VIPs. These
    # are provided by local_pkg_django_setup.
    local_pkg_django_setup.utils.get_ping_check_url_pattern(),

    # Search POST handler. This will be handled by the method in
    # zookawebsite.views.search_view
    url(r'^search$', 'zookawebsite.views.search_view'),

    #host/admin
    url(r'^admin/', include(admin.site.urls)),

    # Homepage handler. This will be handled by the method in
    # zookawebsite.views.homepage_view
    url(r'^$', 'zookawebsite.views.index'),

    # Add the special URL handler for static files. See
    # https://docs.djangoproject.com/en/stable/howto/static-files/ for more
    # information on how static files are served.
    url(
        r'^{prefix}(?P<path>.*)$'.format(prefix=settings.STATIC_URL.lstrip('/')),
        django.views.static.serve,
        {'document_root': settings.STATIC_ROOT}
    ),

########################################################################################################################

    # TTs Cut List
    url(r'^zooka/$', 'zookawebsite.views.zooka', name='tt_list'),

    # Ticket Cutter
    url(r'^zooka/tt-cutter$', 'zookawebsite.views.cutTT', name='initialize_tt'),
    url(r'^zooka/csv-tt-cutter$', 'zookawebsite.views.csvcuttt', name='csv_cut_tt'),

    # TT Updater
    url(r'^zooka/tt-updater$', 'zookawebsite.views.updateTT', name='tt-updater'),
    url(r'^zooka/tts_updated$', 'zookawebsite.views.updated', name='updated'),


    # All Campaigns
    url(r'^zooka/campaigns$', 'zookawebsite.views.campaigns', name='campaigns'),


    # QUnit test suite page.
    url(r'^js-test$', 'zookawebsite.views.js_test_view'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
