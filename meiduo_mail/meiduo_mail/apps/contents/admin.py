from django.contrib import admin
from contents import models
# Register your models here.

admin.site.register(models.Content)
admin.site.register(models.ContentCategory)