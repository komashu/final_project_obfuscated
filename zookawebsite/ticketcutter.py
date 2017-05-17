from obf1 import obf_retrieve, obf_material_retrieve, obf_retrieve_pair, ObfOperationError
from obf3 import F_Client
from obf2.http_auth import HTTPBasicAuth
from obf2 import obf_service
from obf4.w_webservice import W_ServiceClient
from obf4.whitelistentry import WhitelistEntry
from cobf4.ticketsearchinput import TicketSearchInput
from obf4.ticketrecordinput import TicketRecordInput
from cobf4.cclistrecord import CCListRecord
from django.utils import timezone as tz
import pdb
import logging

from .models import *

def now():
    return tz.now

logger = logging.getLogger(__name__)


def get_prod_test_from_campaign(campaign, test=False):
    """
    Based on campaign and if test or not, we set up all the info we need to build the f_client or w_client. It will grab
    the tag, prod_mat, test_mat, f and w endpoints. This is usually called in the client creation and not by itself.
    
    :param campaign: Campaign name which will be used to grab its ID then used to get the tag.
    :param test: Boolean - So we know which endpoints and material sets to use.
    :return: tag, _user, _pass, w_endpoint(Test or prod), f_endpoint(Test or prod)
    """
    campaign = Campaigns.objects.get(campaign=campaign)
    campaign_id = campaign.id
    tag = [str(Tags.objects.filter(campaign_id=campaign_id)),]
    test_mat = campaign.test_mat
    prod_mat = campaign.prod_mat
    if test == True:
        try:
            principal, credential = obf_retrieve_pair(str(test_mat).encode('utf-8'))
            _user = principal.data.decode('utf-8')
            _pass = credential.data.decode('utf-8')
            w_endpoint = 'https://w_obfuscated_test.com'
            f_endpoint = 'https://f_obfuscated_test.com'
            return tag, _user, _pass, w_endpoint, f_endpoint
        except:
            logger.debug('Error gathering creds.')
            return None
    else:
        try:
            principal, credential = obf_retrieve_pair(str(prod_mat).encode('utf-8'))
            _user = principal.data.decode('utf-8')
            _pass = credential.data.decode('utf-8')
            w_endpoint = 'https://w_obfuscated_prod.com/'
            f_endpoint = 'https://f_obfuscated_prod.com'
            return tag, _user, _pass, w_endpoint, f_endpoint
        except:
            logger.debug('Error gathering creds.')
            print('Error gathering creds.')
            return None


def make_w_client(campaign, test):
    """
    Create the client in the views.py to pass the parameters in creating it appropriately. And then pass the client
    into the specific function you are calling for that view. e.g. tt_cut()
    :param campaign(string): Campaign name so we can grab the necessary info to get the tag.
    :param test: Boolean so we know which material sets and endpoints to use.
    :return: w_client. You'll want to call it as w = make_w_client()
    """
    #pdb.set_trace()
    tag, _user, _pass, w_endpoint, f_endpoint = get_prod_test_from_campaign(campaign, test)
    w_timeout = float(5)
    http_auth = HTTPBasicAuth(_user, _pass)
    w_orchestrator = obf_service.new_orchestrator(endpoint=w_endpoint,
                                                 http_auth=http_auth,
                                                 timeout=w_timeout)
    w_client = W_ServiceClient(w_orchestrator)
    return w_client


def f_client(campaign, test):
    """
    Create the client in the views.py to pass the parameters in creating it appropriately. And then pass the client
    into the specific function you are calling for that view. e.g. tt_cut()
    :param campaign(string): Campaign name so we can grab the necessary info to get the tag.
    :param test: Boolean so we know which material sets and endpoints to use.
    :return: a f client
    """
    tag, _user, _pass, w_endpoint, f_endpoint = get_prod_test_from_campaign(campaign, test)
    f = F_Client(user=_user, password=_pass, serverName=f_endpoint)
    return f


def tt_cut(f, username, tag, **ticket_input):
    """
    The actual function that cuts tickets. This is for the one off ticket cutter for now.
    :param f: You should have already created the f client and put it in this function.
    :param username: This should be grabbed by Django in our views using the request.user.username
    :param tag: The tag to use when cutting tickets.
    :param ticket_input: This is a dictionary of all the things that will be used to cut the tickets with the exception
    of the tag.
    :return: id and disposition of the ticket. Plus it adds it to the database.
    """
    _id, disposition = f.createTicket(tags=tag, **ticket_input)
    update_db = Tickets(id=_id,
                        disposition=disposition,
                        created_by=username,
                        tags=tag,
                        **ticket_input)
    update_db.save()
    return _id, disposition


def tt_update(w, campaign, username, **ticket_update):
    """
    Update tickets based on the tag. We use W because there might be instances where the ticket is encrypted. F
    cannot update encrypted tickets. ticket_update will be a dictionary with W legal fields. It can be any W field
    as long as it is formatted as expected. It will also pull out cc_email if it exists and run a separate w call since
    it's a different w function that adds cc's. 
    :param w: The w client you should have already created and passed to this function. 
    :param campaign(string): Campaign name so we can grab the necessary info to get the tag.
    :param username: This should be grabbed by Django in our views using the request.user.username
    :param ticket_update: This is a dictionary of all the things that will be used to update the tickets.
    :return: It will return the tickets and info updated in the next page. Eventually.
    """
    campaign = Campaigns.objects.get(campaign=campaign)
    campaign_id = campaign.id
    tag = str(Tags.objects.get(campaign_id=campaign_id))
    tickets = tag_search(w, tag)
    if ticket_update['cc_email']:
        for t in tickets:
            add_cc(w, t, ticket_update['cc_email'])
    if ticket_update['tags']:
        for t in tickets:
            add_tag(w, t, ticket_update['tag'])
    for t in tickets:
        update = w.modify_ticket(TicketRecordInput(id=t, **ticket_update))
        obj, created = Tickets.objects.update_or_create(id=t,
                                                        defaults={'modified_by': username,
                                                                  'status': ticket_update['status'],
                                                                  'impact': ticket_update['impact'],
                                                                  'correspondence': ticket_update['correspondence'],
                                                                  'cc_email': ticket_update['cc_email'],
                                                                  })
    total_tickets = len(tickets)
    return total_tickets, tickets


def tag_search(w, tags):
    """
    How we get all ticket numbers per tag
    :param w: The w client you should have already created and passed to this function.
    :param tags: The actual tags
    :return: Ticket numbers
    """
    tts = w.solr_search(tags=tags)
    all_tickets = []
    for tt in tts.tickets:
        all_tickets.append(tt.id)
    return all_tickets


def add_tag(w, ticket_id, tag):
    """
    Add tag to a ticket
    :param w: W Client
    :param ticket_id: Ticket ID
    :param tag: The tag you wish to add.
    :return: Will update the ticket with the new tag.
    """
    w.create_tag(ticket_id=ticket_id, tag=tag)


def add_cc(w, ticket, login):
    """
    You can't add CCs with f, so we use a separate call with the w client.
    :param w: The w client you should have already created and passed to this function.
    :param tickets: Ticket id (this should be used in an iteration per ticket.)
    :param login: The login to add to the cc list.
    :return: Updates ticket with CCs.
    """
    ccs = w.add_cc_list(CCListRecord(ticket_id=ticket, emails=login))
    return ccs


def remove_cc(w, ticket, login):
    """
    Remove CCs by name and ticket.
    :param w: The w client you should have already created and passed to this function.
    :param ticket: Ticket id (this should be used in an iteration per ticket.)
    :param login: The login to remove to the cc list.
    :return: Updates the ticket removing the CC
    """
    ccs = w.remove_cc_list(CCListRecord(ticket_id=ticket, emails=login))
    return ccs


def tt_csv_cut(f, tag, **ticket_input):
    """
    This is special for CSV uploads only. It's just like tt_cut() but with added functionality to handle a csv file.
    :param f: You should have already created the f client and put it in this function. We also aren't updating
    the models here like in tt_cut()
    :param tag: Tag to use
    :param ticket_input: This is a dictionary of all the things that will be used to cut the tickets with the exception
    of the tag.
    :return: id and disposition of tickets created.
    """
    _id, disposition = f.createTicket(tags=tag, **ticket_input)
    return _id, disposition


def uploaded_csv(f, w, username, header, tag, _file):
    """
    This handles the uploaded csv file. First it will lower case the headers to match the model fields. Then we zip and
    map it all into a dictionary. It will then loop and cut the ticket. But if there needs to be a cc added, it will break
    off and do that after the ticket is created. And the loop finishes with updating it into our database.
    :param f: You should have already created the f client and put it in this function.
    :param w: The w client you should have already created and passed to this function.
    :param username: This should be grabbed by Django in our views using the request.user.username
    :param header: This is the header from the csv file to become the keys in a dictionary.
    :param tag: Tag name to use.
    :param _file: Actual file opened with csv.reader.
    :return: Creates the ticket, adds cc if there in separate call and then updates the model database.
    """
    header = [item.lower() for item in header]
    all_tickets = [dict(zip(header, map(str, row))) for row in _file]
    created_tickets = []
    ticket_count = len(all_tickets)
    for ticket in all_tickets:
        _id, disposition = tt_csv_cut(f, tag, **ticket)
        if ticket['cc_email']:
            email = ticket['cc_email']
            add_cc(w, id, email )
        _, created = Tickets.objects.get_or_create(id=id, created_by=username, disposition=disposition, **ticket)
        ticket.update({'ticket_id': _id})
        created_tickets.append(ticket)
    return ticket_count, created_tickets


def get_eticket(w, id):
    """
    This is how we get the eticket # for tickets that were later converted and our access was removed.
    :param id: The non-e-ticket id number
    :return: the new e-ticket number
    """
    try:
        result = w.get_ticket(id)
        return result
    except Exception as e:
        result = str(e).split(':')[5].strip('>').strip(')').strip('"')
        return result

def get_resolver_grp_manager(w, tt):
    """
    How we can grab the owner/manager of the resolver group of a ticket.
    :param w: The w client
    :param tt: The ticket number
    :return: Resolver group manager username
    """
    resolver_group = w.solr_search_ticket(id=tt).tickets[0].assigned_group
    group = w.search_people_group_details(login_name=resolver_group)
    rg_manager = group.result_list[0].manager_login
    return rg_manager

def get_ticket_count():
    campaigns = Campaigns.objects.all().prefetch_related('tagz')
    for item in campaigns:
        pass




