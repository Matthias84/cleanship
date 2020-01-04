from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import generic
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from common.models import Issue, IssueFilter, StatusTypes, TrustTypes
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = Issue.objects.filter(pk=self.kwargs.get('pk'))[0]
        trustMapping = {TrustTypes.INTERNAL: "internal", TrustTypes.EXTERNAL: "external", TrustTypes.FIELDTEAM: "fieldteam"}
        context['author_trust_string'] = trustMapping[issue.authorTrust]
        statusMapping = {StatusTypes.SUBMITTED: "submitted",
                        StatusTypes.WIP: "wip",
                        StatusTypes.SOLVED: "solved",
                        StatusTypes.IMPOSSIBLE: "impossible",
                        StatusTypes.DUBLICATE: "dublicate"}
        context['status_string'] = statusMapping[issue.status]
        positionWGS84 = issue.position
        positionWGS84.transform(4326)
        positionWGS84 = positionWGS84.geojson
        context['position_geojson'] = positionWGS84
        return context

class IssueListView(SingleTableMixin, FilterView):
    model = Issue
    table_class = IssueTable
    filterset_class = IssueFilter
    template_name = 'office/issues.html'
    
    def get_queryset(self):
        """List all assigned issues"""
        return Issue.objects.filter(assigned__in=self.request.user.groups.all())
