from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(BlogPost)
admin.site.register(category)
admin.site.register(Tag)
admin.site.register(Reaction)
admin.site.register(Report)
admin.site.register(Comment)