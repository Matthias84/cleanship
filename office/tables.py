import django_tables2 as tables
from common.models import Issue

class IssueTable(tables.Table):
    created_at = tables.DateColumn()
    id = tables.Column(linkify=("office:issue", {"pk": tables.A("pk")}))
    category_type = tables.Column()
        
    def category_maincat(self, issue):
        return issue.category.parent.name
    
    def render_category_subcat(self, value, record):
        issue = record
        return issue.category.name
    
    def render_category_type(self, value, record):
        # TODO: Merge with admin code
        print(record)
        issue = record
        if issue.category.get_root().name == 'Problem':
                return '❗'
        if issue.category.get_root().name == 'Idee':
            return '💡'
        if issue.category.get_root().name == 'Tipp':
            return '👆'
    
    class Meta:
        model = Issue
        template_name = "django_tables2/bootstrap4.html"
        fields = ('id', 'created_at', 'location', 'category_type', 'category_subcat', 'priority', 'status_styled','status_created_at', 'published' )
        order_by = ('-id')
        attrs = {
                'class': 'table table-hover',
                'thead' : {
                    'class': 'thead-light'
                }
        }
