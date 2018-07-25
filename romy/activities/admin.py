from django.contrib import admin

from .models import Baby, Activity

class BabyAdmin(admin.ModelAdmin):
    readonly_fields = ('api_key', 'last_activity')
    list_display = ('first_name', 'parent', 'api_key', 'last_activity')

admin.site.register(Baby, BabyAdmin)


class ActivityAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'last_connection')
    list_display = ('id', 'baby', 'type', 'created_date')

    search_fields = ['parent']

admin.site.register(Activity, ActivityAdmin)
