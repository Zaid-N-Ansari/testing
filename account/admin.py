from django.contrib import admin
from .models import UserAccount

class UserAccountAdmin(admin.ModelAdmin):
	readonly_fields = [field.name for field in UserAccount._meta.fields]

	list_display = ('username','id')

admin.site.register(UserAccount, UserAccountAdmin)
