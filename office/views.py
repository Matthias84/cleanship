from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import generic
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from common.models import Issue, IssueFilter
from .tables import IssueTable

@login_required
def start(request):
    l = []
    for g in request.user.groups.all():
        l.append(g.name)
    return render(request, 'office/start.html', {'groups': l})


class IssueDetailView(generic.DetailView):
    model = Issue
    template_name = 'office/issue.html'

class IssueListView(SingleTableMixin, FilterView):
    model = Issue
    table_class = IssueTable
    filterset_class = IssueFilter
    template_name = 'office/issues.html'
    
    def get_queryset(self):
        """List all assigned issues"""
        return Issue.objects.filter(assigned__in=self.request.user.groups.all())
