from django.contrib import admin
from .models import UserAccount

class UserAccountAdmin(admin.ModelAdmin):
	readonly_fields = ('id','password')
	list_display = ('username','id')

admin.site.register(UserAccount, UserAccountAdmin)
