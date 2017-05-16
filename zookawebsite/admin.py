from django.contrib import admin
from .models import *


class TicketsAdmin(admin.ModelAdmin):
    list_display = ['short_description',
                    'details',
                    'requester_login',
                    'cc_list',
                    'tag',
                    'category',
                    'type',
                    'item',
                    'requester_name',
                    'impact',
                    'id',
                    'disposition'
                    ]
    search_fields = ['id',
                     'requester_login',
                     'tag'
                     'impact'
                     'disposition'
                     ]

class ProdMatsAdmin(admin.ModelAdmin):
    model = ProdMats
    fields = ['prod_mats']

class TestMatsAdmin(admin.ModelAdmin):
    model = TestMats
    fields = ['test_mats']

class TagsAdmin(admin.ModelAdmin):
    model = Tags
    fields = ['tag']
    exclude = ['campaign']

class TagsInLine(admin.TabularInline):
    model = Tags
    extra = 2

class CampaignsAdmin(admin.ModelAdmin):
    model = Campaigns
    list_display = ['campaign', 'prod_mat', 'test_mat']
    fields = ['campaign', 'prod_mat', 'test_mat', 'created_by']
    inlines = [TagsInLine,]



admin.site.register(Tickets)
admin.site.register(Campaigns, CampaignsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(ProdMats)
admin.site.register(TestMats)
