from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, Issue, Category


class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['email', 'username']


class IssueAdmin(admin.GeoModelAdmin):
        readonly_fields = ["thumb_image"]

        def thumb_image(self, obj):
                return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.photo.url,
                    width=obj.photo.width,
                    height=obj.photo.height,
                    )
                )


admin.site.register(User, UserAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Category, MPTTModelAdmin)
