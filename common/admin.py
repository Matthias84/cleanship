from django.contrib import admin as adminorg
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter
from leaflet.admin import LeafletGeoAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, Issue, Category, Comment, Feedback


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
        readonly_fields = ['id', 'thumb_image', 'location', 'landowner']
        date_hierarchy = 'created_at'
        list_display = ('id', 'created_at', 'location', 'category_type', 'category_subcat', 'priority', 'status', 'published')
        list_filter = ('created_at', 'priority', 'status', 'published', ('category', TreeRelatedFieldListFilter),) # TODO: split category levels for filters #47
        search_fields = ['id', 'location']
        # TODO: Add admin bulk actions #10
        # TODO: Add Link to public frontend / backoffice view_on_site() #11
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
        inlines = [FeedbackInline, CommentInline]


        def thumb_image(self, obj):
                return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.photo.url,
                    width=obj.photo.width,
                    height=obj.photo.height,
                    )
                )
        
        def category_type(self, issue):
            return issue.category.get_root().name
        
        def category_maincat(self, issue):
            return issue.category.parent.name
        
        def category_subcat(self, issue):
            return issue.category.name

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
