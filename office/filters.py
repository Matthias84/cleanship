from django import forms
from django.utils.translation import gettext_lazy as _
import django_filters

from common.models import Issue, Group, StatusTypes

class IssueFilter(django_filters.FilterSet):
    author_email = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    landowner = django_filters.CharFilter(lookup_expr='icontains')
    create_between = django_filters.DateFromToRangeFilter(field_name='created_at', widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'}))
    # TODO: useful Date ranges e.g. 30d, 1y, ... (daterangefilter)
    category__name = django_filters.CharFilter(lookup_expr='icontains')
    assigned = django_filters.ModelMultipleChoiceFilter(
        queryset=Group.objects.all().order_by('name'),
        widget=forms.SelectMultiple(),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=StatusTypes.choices(),
        widget=forms.CheckboxSelectMultiple(),
        )

    class Meta:
        model = Issue
        # TODO: category, delegated
        fields = ['id', 'assigned', 'author_trust', 'location', 'priority', 'landowner', 'status', 'published']
    
    def __init__(self, data, *args, **kwargs):
        # set default fields if not other requested
        super().__init__(data, *args, **kwargs)
        self.form.initial['status'] = [int(StatusTypes.WIP), int(StatusTypes.REVIEW)]
        self.form.initial['assigned'] = self.request.user.groups.all()
