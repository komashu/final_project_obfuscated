from django import forms
from django.forms import Form, Textarea, HiddenInput
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from django.forms.formsets import BaseFormSet
from django.forms.models import inlineformset_factory

from .models import *


impchoices = [('', '' ), ('5', 'Sev 5'), ('4', 'Sev 4'), ('3','Sev 3'), ('2','Sev 2.5'), ('1','Sev 2')]
status_choices = [('', ''), ('Assigned', 'Assigned'), ('Researching', 'Researching'), ('Work In Progress','Work In Progress'), ('Pending', 'Pending'), ('Resolved', 'Resolved')]

class CutTicketForm(forms.Form):
    short_desc = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    details = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 6}), required=False)
    category = forms.CharField(initial='Technical Risk Reduction', widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    type = forms.CharField(initial='Enterprise Campaign Management', widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    item = forms.CharField(initial='Infrastructure and Tools', widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    assigned_group =  forms.CharField(initial='Enterprise Campaign Management', widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    cc_list = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    requester_login = forms.CharField(initial='ecm-user', widget=forms.Textarea(attrs={'cols': 20, 'rows': 1}), required=False)
    requester_name = forms.CharField(initial='ecm-user', widget=forms.Textarea(attrs={'cols': 20, 'rows': 1}), required=False)
    impact = forms.ChoiceField(choices=impchoices, required=False)
    dedupe_string = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    submitter = forms.CharField(initial='ecm-user', widget=forms.Textarea( attrs={'cols': 20, 'rows': 1}), required=False)
    campaign = forms.ModelChoiceField(Campaigns.objects.all())
    test = forms.BooleanField(widget=forms.NullBooleanSelect(), required=False)
    created_by = forms.HiddenInput()


    #def get_campaign_items(self):
    #    campaign_id = campaign.id
    #    tag = Tags.objects.get(campaign_id=campaign_id)
    #    prod_mat = campaign.prod_mat
    #    test_mat = campaign.test_mat
    #    return tag, prod_mat, test_mat

class CSVTTCutterForm(forms.Form):
    campaign = forms.ModelChoiceField(Campaigns.objects.all())
    test = forms.BooleanField(widget=forms.NullBooleanSelect(), required=True)
    upload = forms.FileField(required=True)
    created_by = forms.HiddenInput()

class UpdateTicketsForm(forms.Form):
    status = forms.ChoiceField(choices=status_choices, required=False)
    cc_email = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}), required=False)
    correspondence = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 6}), required=False)
    add_tag = forms.CharField(widget=forms.Textarea(attrs={'cols': 100, 'rows': 1}), required=False)
    impact = forms.ChoiceField(choices=impchoices, required=False)
    campaign = forms.ModelChoiceField(queryset=Campaigns.objects.all())
    test = forms.BooleanField(widget=forms.NullBooleanSelect(), required=False)
    modified_by = forms.HiddenInput()


