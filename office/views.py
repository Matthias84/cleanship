from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import generic
from django_tables2 import SingleTableView

from common.models import Issue
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

class IssueListView(SingleTableView):
    model = Issue
    table_class = IssueTable
    template_name = 'office/issues.html'
    
    def get_queryset(self):
        """List all assigned issues"""
        return Issue.objects.filter(assigned__in=self.request.user.groups.all())
