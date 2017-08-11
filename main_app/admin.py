from django.contrib import admin
from main_app.models import sites, statuses, redirects
# Register your models here.
admin.site.register(statuses)
admin.site.register(sites)
admin.site.register(redirects)