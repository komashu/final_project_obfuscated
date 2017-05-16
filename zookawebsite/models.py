from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone as tz

def now():
    return tz.now

class ProdMats(models.Model):
    prod_mats = models.CharField(
        'Prod Material',
        max_length=80,
        default='obfuscated_material_set_prod',
        null=False
    )

    def __str__(self):
        return self.prod_mats

    class Meta:
        verbose_name_plural = "ProdMats"


class TestMats(models.Model):
    test_mats = models.CharField(
        'Test Material',
        max_length=80,
        default='obfuscated_material_set_test',
        null=False
    )

    def __str__(self):
        return self.test_mats

    class Meta:
        verbose_name_plural = "TestMats"

class Campaigns(models.Model):
    """
    Campaigns for selecting when cutting tickets or updating them. Materials are tied by foreign keys and tags are
    separate so campaigns can have more than one tag. (Tags will have a foreign key pointing here.) Use the admin site
    to add them.
    """
    campaign = models.CharField('Campaign', max_length=80, null=False)
    prod_mat = models.ForeignKey(ProdMats, null=False)
    test_mat = models.ForeignKey(TestMats, null=False)
    created_by = models.ForeignKey(User, blank=False)
    created_on = models.DateTimeField(default=now())

    def __str__(self):
        return self.campaign


    def get_absolute_url(self):
        return reverse('campaign_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = "Campaigns"


class Tags(models.Model):
    tag = models.CharField('Tag', max_length=120, unique=True, null=False)
    campaign = models.ForeignKey(Campaigns, related_name='tagz')

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name_plural = "Tags"


class Tickets(models.Model):
    """
    For ticket tracking. Built in a lot of fields for future build out for something like Lighthouse, mostly for tracking
    what we cut or update. But could build out on the fly info on tickets too without storing. So this is more for future 
    use
    """
    category = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, null=False)
    item = models.CharField(max_length=255, null=False)
    assigned_group = models.CharField(max_length=255, null=False)
    assigned_individual = models.CharField(max_length=255, null=False)
    status = models.CharField(max_length=80, null=False)
    pending = models.CharField(max_length=255, null=True)
    short_description = models.CharField(max_length=255, null=False)
    details = models.CharField(max_length=255, null=False)
    cc_email = models.CharField(max_length=255, null=True)
    related = models.CharField(max_length=255, null=True)
    tags = models.CharField(max_length=255, null=False)
    correspondence = models.TextField(max_length=255, null=False)
    work_log = models.CharField(max_length=255, null=False)
    eticket = models.NullBooleanField()
    requester_login = models.CharField(max_length=80, null=False)
    disposition = models.CharField(max_length=255, null=False)
    id = models.CharField(max_length=100, null=False, primary_key=True)
    impact = models.CharField(max_length=3, null=False)
    requester_name = models.CharField(max_length=80, null=False)
    dedupe_string = models.CharField(max_length=255, null=True)
    submitter = models.CharField(max_length=255, null=True)
    date_submitted = models.DateTimeField(default=now())
    last_modified = models.DateTimeField(default=now())
    created_by = models.CharField(max_length=80, null=False)
    modified_by = models.CharField(max_length=80, null=True)


    def __str__(self):
        return self.id

    class Meta:
        verbose_name_plural = "Tickets"

