from django.contrib import admin as adminorg
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter
from leaflet.admin import LeafletGeoAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, Issue, Category, Comment, Feedback, StatusTypes


class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['email', 'username']

class CommentInline(admin.StackedInline):
    model = Comment
    ordering = ['-created_at']
    readonly_fields = ['created_at', "content", "author"]
    extra = 0

class FeedbackInline(admin.StackedInline):
    model = Feedback
    ordering = ['-created_at']
    readonly_fields = ['created_at', "content", "authorEmail"]
    extra = 0

class IssueAdmin(LeafletGeoAdmin):
        readonly_fields = ['id', 'thumb_image', 'location', 'landowner', 'authorTrust', 'status_created_at']
        date_hierarchy = 'created_at'
        list_display = ('id', 'created_at', 'location', 'category_type', 'category_subcat', 'priority', 'status_styled','status_created_at', 'published')
        list_filter = ('created_at', 'priority', 'status', 'published', 'authorTrust', ('category', TreeRelatedFieldListFilter),) # TODO: split category levels for filters #47
        search_fields = ['id', 'location']
        # TODO: Add admin bulk actions #10
        # TODO: Add Link to public frontend / backoffice view_on_site() #11
        fieldsets = (
        ('Basics', {
            'fields': ( 'id', 'created_at', 'authorEmail', 'authorTrust', 'category', 'description', 'thumb_image', 'photo')
        }),
        ('Geospatial', {
            #'classes': ('collapse',),
            'fields': ('position', 'location', 'landowner'),
        }),
        ('Processing', {
            'fields': ('priority', 'status_created_at', 'status', 'status_text', 'assigned', 'delegated'),
        }),
        )
        inlines = [FeedbackInline, CommentInline]

        def thumb_image(self, obj):
                return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.photo.url,
                    width=obj.photo.width,
                    height=obj.photo.height,
                    )
                )
        
        def status_styled(self, obj):
            if obj.status == StatusTypes.SUBMITTED:
                color = 'grey'
            elif obj.status == StatusTypes.WIP:
                color = 'red'
            else:
                color = 'green'
            return mark_safe('<div style="width:100%%; height:100%%; background-color:%s;">%s</div>' % (color, obj.get_status_display()))
        
        def category_type(self, issue):
            if issue.category.get_root().name == 'Problem':
                return '❗'
            if issue.category.get_root().name == 'Idee':
                return '💡'
            if issue.category.get_root().name == 'Tipp':
                return '👆'
        
        def category_maincat(self, issue):
            return issue.category.parent.name
        
        def category_subcat(self, issue):
            return issue.category.name
        
        status_styled.short_description = 'status'
        category_type.short_description = 'type'

class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('issue_id', 'created_at', 'author')
    list_filter = ('author',)
    search_fields = ['issue_id','author' ]
    
    def issue_id(self, obj):
        return obj.issue.id

class FeedbackAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('issue_id', 'created_at', 'authorEmail')
    list_filter = ('authorEmail',)
    search_fields = ['issue_id','authorEmail' ]
    
    def issue_id(self, obj):
        return obj.issue.id

admin.site.register(User, UserAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Feedback, FeedbackAdmin)
