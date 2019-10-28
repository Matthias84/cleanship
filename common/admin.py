from django.contrib.gis import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, Issue, Category

class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['email', 'username',]

admin.site.register(User, UserAdmin)
admin.site.register(Issue, admin.GeoModelAdmin)
admin.site.register(Category , MPTTModelAdmin)
