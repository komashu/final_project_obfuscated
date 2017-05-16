"""
This module contains all the views supported in the Django app. These are
nothing more than Python methods which always take the
django.http.HttpRequest class as their first argument and return a
django.http.HttpResponse class or a subclass of it.

See https://docs.djangoproject.com/en/stable/ref/request-response/ for
more information about request objects received and response object to
return.

See https://docs.djangoproject.com/en/stable/topics/http/shortcuts/ for
information about shortcut methods like the :meth:`django.shortcuts.render`
method which is helpful in rendering a response from a Django template.
"""
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render, redirect, render_to_response
from django.core.files.storage import FileSystemStorage
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView
import csv
from .forms import *
from zookawebsite.decorators import get_user
from .ticketcutter import *
from .models import *
import pdb
import logging

# TO DO - make function that gets ticket info for page. make another function to get modify dates of tickets recently
# for the tickets updated page to verify they were updated.

logger = logging.getLogger(__name__)

def index(request):
    """
    Nothing here right now. Holding spot.
    :param request: 
    :return: 
    """
    u = request.user.username
    username = u.split("@")[0]
    context = {'username': username

    }
    return render(request,
        'zookawebsite/index.html', context)


def zooka(request):
    """
    Lists all cut and updated tickets
    :param request: 
    :return: List of tickets with links to the odin set and link to all tickets by tag.
    """
    u = request.user.username
    username = u.split("@")[0]
    tickets = Tickets.objects.all()
    header = 'Tickets'
    context = {'username': username,
               'tickets': tickets,
               'header': header
    }
    return render(request, 'zookawebsite/zooka.html', context)


@staff_member_required
def cutTT(request):
    """
    Cuts a f ticket then updates the ticket information into the model database. 
    
    TODO: Add the csv option to combine methods.
    
    :param request:
    :return: Created ticket info, id, disposition
    """
    u = request.user.username
    username = u.split("@")[0]
    form = CutTicketForm()
    header = 'Ticketer'
    context = {
        'username': username,
        'form': form,
        'header': header
    }
    if request.method == 'POST':
        form = CutTicketForm(request.POST or None)
        if form.is_valid():
            short_desc = form.cleaned_data['short_desc']
            details = form.cleaned_data['details']
            requester_login = form.cleaned_data['requester_login']
            cc_list = form.cleaned_data['cc_list']
            category = form.cleaned_data['category']
            type = form.cleaned_data['type']
            item = form.cleaned_data['item']
            assigned_group = form.cleaned_data['assigned_group']
            requester_name = form.cleaned_data['requester_name']
            submitter = form.cleaned_data['submitter']
            dedupe_string = form.cleaned_data['dedupe_string']
            campaign = form.cleaned_data['campaign']
            test = form.cleaned_data['test']
            impact = form.cleaned_data['impact']
            ticket_input = {'short_description': short_desc,
                            'details': details,
                            'requester_login': requester_login,
                            'category': category,
                            'type': type,
                            'item': item,
                            'requester_name': requester_name,
                            'impact': impact,
                            'assigned_group': assigned_group,
                            'dedupe_string': dedupe_string,
                            'submitter': submitter
                            }
            f = f_client(campaign, test)
            w = make_w_client(campaign, test)
            campaign_id = campaign.id
            tag = str(Tags.objects.get(campaign_id=campaign_id))
            id, dispostion = tt_cut(f, username, tag, **ticket_input)
            if cc_list:
                add_cc(w, id, cc_list)
            return redirect(reverse('tt_list'))
        else:
            logger.debug('Form is not valid', username)
            return render(request, 'zookawebsite/forms.html', context)
    else:
        logger.debug('Request is not POST', username)
        return render(request, 'zookawebsite/forms.html', context)


@staff_member_required
def csvcuttt(request):
    """
    To cut tickets via a csv file by campaign. You would select the campaign and gets the material sets plus tag to use.
    We create both the f and w client because cc adding has to be done with w.
    
    The file will be saved to an upload folder, then we grab the headers so we can make a dictionary. We do it this way
    so it doesn't matter what order and what fields people use, gives flexibility. We will also 
    grab the campaign id so we can grab the tags for cutting. Then we pass it to the ticketcutter module.
    
    TODO: Make the success page to show what was updated. Fix error handling. I would like to also combine this with
    the other form so we can mix and match the csv data with things from the form.
    
    :param request: 
    :return: Cuts tickets en masse, add to db.
    """
    u = request.user.username
    username = u.split("@")[0]
    form = CSVTTCutterForm()
    header = 'CSV Ticketer'
    context = {
        'username': username,
        'form': form,
        'header': header
    }
    if request.method == 'POST' and request.FILES['upload']:
        data = CSVTTCutterForm(request.POST, request.FILES)
        if data.is_valid():
            uploaded_file = request.FILES['upload']
            fs = FileSystemStorage(location='/tmp/')
            savingfile = fs.save(uploaded_file.name, uploaded_file)
            csvfile= open('/tmp/' + savingfile, 'rt')
            _file = csv.reader(csvfile, dialect=csv.excel)
            header = next(_file)
            campaign = data.cleaned_data['campaign']
            test = data.cleaned_data['test']
            f = f_client(campaign, test)
            w = make_w_client(campaign, test)
            campaign_id = campaign.id
            tag = str(Tags.objects.get(campaign_id=campaign_id))
            uploaded_csv(f, w, username, header, tag, _file)
            return redirect(reverse('tt_list'))
        else:
            logger.debug('Data is not valid', username)
            return render(request, 'zookawebsite/forms.html', context)
    else:
        logger.debug('Request method was not POST and/or no file uploaded', username)
        return render(request, 'zookawebsite/forms.html', context)


@staff_member_required
def updateTT(request):
    """
    Here you can update tickets by a tag. You will be able to change status, impact, add cc, and correspondence. 
    Eventually we will add more features like escalate to manager, escalate to level. This will also update or add
    the updates to the ticket in the site's db.
    :param request: 
    :return: Update tickets by tag. Save to models.
    """
    u = request.user.username
    username = u.split("@")[0]
    form = UpdateTicketsForm()
    tickets = Tickets.objects.all().order_by('last_modified')
    header = 'Updater'
    context = RequestContext(request, {
        'username': username,
        'form': form,
        'header': header,
        'tickets': tickets,
    })
    if request.method == 'POST':
        form = UpdateTicketsForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            cc_email = form.cleaned_data['cc_email']
            impact = form.cleaned_data['impact']
            tags = form.cleaned_data['add_tag']
            correspondence = form.cleaned_data['correspondence']
            campaign = form.cleaned_data['campaign']
            test = form.cleaned_data['test']
            ticket_update = {
                'status': status,
                'impact': impact,
                'tags': tags,
                'correspondence': correspondence,
                'cc_email': cc_email,
            }
            w = make_w_client(campaign, test)
            tt_update(w, campaign, username, **ticket_update)
            return render_to_response('zookawebsite/zooka.html', context)
        else:
            logger.debug(form.errors())
            logger.debug('Form is not valid', username)
            return form.errors()
    else:
        logger.debug('Request was not POST', username)
        return render(request, 'zookawebsite/forms.html', context)


def updated(request):
    # TO DO - make page show tickets that were updated, create template too.
    return render(request, 'zookawebsite/updated.html')


def campaigns(request):
    """
    Shows list of campaigns
    :param request: 
    :return: A website that joins the tags with the campaigns
    """
    u = request.user.username
    username = u.split("@")[0]
    campaigns = Campaigns.objects.all().prefetch_related('tagz')
    header = 'Campaigns'
    context = {
        'username': username,
        'header': header,
        'campaigns': campaigns,
    }
    return render(request, 'zookawebsite/campaigns.html', context)


def search_view(request):
    """
    Return search view.

    :param request: Django HTTP request.
    :type request: django.http.HttpRequest
    :return: Django response
    :rtype: django.http.HttpResponse
    """
    # Send a 405 response if this is not a POST request.
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # NOTE: Basic template site doesn't contain anything except for the home
    # page therefore the output returned from the search view is minimal.
    # Once the site starts growing and becoming more complex, the search
    # functionality implemented here should be updated accordingly.
    json_data = {}
    json_data['uriLookup'] = {}
    json_data['uriLookup']['About'] = {}
    json_data['uriLookup']['About']['uri'] = ""
    json_data['uriLookup']['Home'] = {}
    json_data['uriLookup']['Home']['uri'] = ""
    json_data['names'] = []
    for key in json_data['uriLookup']:
        json_data['names'].append(key)
    return JsonResponse(json_data)


def js_test_view(request):
    """
    Return JavaScript test page.

    :param request: Django HTTP request.
    :type request: django.http.HttpRequest
    :return: Django response
    :rtype: django.http.HttpResponse
    """
    if not settings.DEBUG:
        # Don't enable the JS test page in production environments.
        raise PermissionDenied
    context = {
        'jquery_js_url': settings.JQUERY_JS_URL,
        'oneg_css_url': settings.ONEG_CSS_URL,
        'oneg_js_url': settings.ONEG_JS_URL,
        'qunit_css_url': settings.QUNIT_CSS_URL,
        'qunit_js_url': settings.QUNIT_JS_URL,
    }
    return render(request,
        'zookawebsite/js-test.html', context)



