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
        readonly_fields = ['id', "thumb_image"]
        date_hierarchy = 'created_at'
        list_display = ('id', 'created_at', 'location', 'category', 'priority', 'status')
        list_filter = ('created_at', 'priority', 'status', 'category') # TODO: split category levels for filters
        search_fields = ['id']
        # TODO: Add admin bulk actions
        # TODO: Add Link to public frontend / backoffice view_on_site()
        fieldsets = (
        ('Basics', {
            'fields': ( 'id', 'created_at', 'authorEmail', 'category', 'description', 'thumb_image', 'photo')
        }),
        ('Geospatial', {
            #'classes': ('collapse',),
            'fields': ('position', 'location', 'landowner'),
        }),
        ('Processing', {
            'fields': ('priority', 'status', 'assigned', 'delegated'),
        }),
        )

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
