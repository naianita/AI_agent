from django.contrib import admin
from .models import User_Info
from django.utils.timezone import localtime
import pytz

# Register your models here.

@admin.register(User_Info)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'mtext', 'response', 'display_vancouver_time', 'pic_url')
    search_fields = ('uid', 'name', 'mtext', 'response')
    list_filter = ('mdt',)

    def display_vancouver_time(self, obj):
        vancouver_tz = pytz.timezone('America/Vancouver')
        return localtime(obj.mdt, vancouver_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    display_vancouver_time.short_description = 'MDT (Vancouver Time)'


