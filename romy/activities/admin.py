from django.contrib import admin

from .models import Baby, Activity, BetaUser


class BetaUserAdmin(admin.ModelAdmin):
    readonly_fields = ('email', 'signup_date')
    list_display = ('id', 'email', 'signup_date')

admin.site.register(BetaUser, BetaUserAdmin)

class BabyAdmin(admin.ModelAdmin):
    readonly_fields = ('api_key', 'last_activity')
    list_display = ('first_name', 'api_key', 'last_activity')

admin.site.register(Baby, BabyAdmin)


class ActivityAdmin(admin.ModelAdmin):
    readonly_fields = ['last_connection']
    list_display = ('id', 'baby', 'type', 'comment', 'parent', 'created_date')

    search_fields = ['parent']

admin.site.register(Activity, ActivityAdmin)
