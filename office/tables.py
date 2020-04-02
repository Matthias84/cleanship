from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from common.models import Issue, StatusTypes

class IssueTable(tables.Table):
    created_at = tables.DateColumn()
    status_created_at = tables.DateColumn()
    id = tables.Column(linkify=("office:issue", {"pk": tables.A("pk")}), verbose_name= _('number'))
    category = tables.Column()
    category_type = tables.Column(empty_values=(), verbose_name= _('category type'))
    category_main = tables.Column(empty_values=(), verbose_name= _('main category'))
    category_sub = tables.Column(empty_values=(), verbose_name= _('sub category'))
    status_styled = tables.Column(empty_values=(), verbose_name= _('status'))
    
        
    def render_category_main(self, record):
        issue = record
        return issue.category.parent.name
    
    def render_category_sub(self, value, record):
        issue = record
        return issue.category.name
    
    def render_category_type(self, value, record):
        # TODO: Merge with admin code
        issue = record
        type_text = issue.category.get_root().name
        if type_text == 'Problem':
            return mark_safe('<i class="fa fa-warning" aria-hidden="true" title="{}"></i>'.format(type_text))
        if type_text == 'Idee':
            return mark_safe('<i class="fa fa-lightbulb-o" aria-hidden="true" title="{}"></i>'.format(type_text))
        if type_text == 'Tipp':
            return mark_safe('<i class="fa fa-flash" aria-hidden="true" title="{}"></i>'.format(type_text))
    
    def render_status_styled(self, value, record):
        issue = record
        status_text = issue.get_status_display()
        if issue.status == StatusTypes.SUBMITTED:
            return mark_safe('<i class="fa fa-share text-muted" aria-hidden="true" title="{}"></i>'.format(status_text))
        elif issue.status == StatusTypes.REVIEW:
            return mark_safe('<i class="fa fa-share text-danger" aria-hidden="true" title="{}"></i>'.format(status_text))
        elif issue.status == StatusTypes.WIP:
            return mark_safe('<i class="fa fa-gears text-danger" aria-hidden="true" title="{}"></i>'.format(status_text))
        elif issue.status == StatusTypes.SOLVED:
            return mark_safe('<i class="fa fa-flag-checkered text-success" aria-hidden="true" title="{}"></i>'.format(status_text))
        elif issue.status == StatusTypes.IMPOSSIBLE:
            return mark_safe('<i class="fa fa-flag-checkered text-success" aria-hidden="true" title="{}"></i>'.format(status_text))
        elif issue.status == StatusTypes.DUBLICATE:
            return mark_safe('<i class="fa fa-copy text-muted"" aria-hidden="true" title="{}"></i>'.format(status_text))
    class Meta:
        model = Issue
        template_name = "django_tables2/bootstrap4.html"
        fields = ('id', 'created_at', 'location', 'category_type', 'category_sub', 'priority', 'status_styled','status_created_at', 'published' )
        order_by = ('-id')
        attrs = {
                'class': 'table table-hover',
                'thead' : {
                    'class': 'thead-light'
                }
        }
