from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Cable)
admin.site.register(models.Interface)
admin.site.register(models.Console)
admin.site.register(models.DataSocket)
admin.site.register(models.Device)
