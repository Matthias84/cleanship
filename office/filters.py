import django_filters

from common.models import Issue

class IssueFilter(django_filters.FilterSet):
    author_email = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    landowner = django_filters.CharFilter(lookup_expr='icontains')
    create_between = django_filters.DateFromToRangeFilter(field_name='created_at', widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'}))
    # TODO: useful Date ranges e.g. 30d, 1y, ... (daterangefilter)
    category__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Issue
        # TODO: category, delegated
        fields = ['id', 'author_trust', 'location', 'priority', 'landowner', 'status', 'published']
    
    def __init__(self, data, *args, **kwargs):
        if not data:
            data = {}
            data['published'] = 'True'
            data['status'] = '2'
        else:
            if not data.get('published'):
                if not data.get('foo'):
                    data = data.copy()
                    data['published'] = 'True'
                    data['status'] = '2'
        super().__init__(data, *args, **kwargs)
