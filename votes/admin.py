from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import Poll, Choice, Vote

class Myadminsite(AdminSite):
	site_header = 'voting system'

adminsite= Myadminsite(name = 'my-site-admin')

adminsite.register(Poll)
adminsite.register(Choice)
adminsite.register(Vote)

admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Vote)
