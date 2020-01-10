from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from leaflet.forms.widgets import LeafletWidget

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
        """List all assigned and filtered issues"""
        return Issue.objects.filter(assigned__in=self.request.user.groups.all())

    def get_context_data(self,**kwargs):
        """Extend with improved map representation"""
        context = super().get_context_data(**kwargs)
        # reproject
        for issue in context['object_list']:
            positionWGS84 = issue.position
            positionWGS84.transform(4326)
            issue.position_webmap = positionWGS84.geojson
        return context

class IssueCreateView(generic.CreateView):
    model = Issue
    fields = ['description', 'category', 'authorEmail', 'position','photo']
    template_name = 'office/issue_create.html'
    
    def get_form(self):
        form = super(IssueCreateView, self).get_form()
        form.fields['position'].widget = LeafletWidget()
        form.fields['authorEmail'].help_text = 'eMail of subitter (usually a citizen, will get a info mail. No confirmation nessesary)'
        form.fields['position'].help_text = 'Try to map the position as accurate as possible (used to determine landowner and location description)'
        form.fields['photo'].help_text = 'Photo showing the spot and surroundings'
        return form
        
    def get_initial(self):
        initial = super(IssueCreateView, self).get_initial()
        initial = initial.copy()
        initial['authorEmail'] = self.request.user.email
        return initial
    
    def form_valid(self, form):
        # Set issue defaults if submitted via office users
        self.object = form.save(commit=False)
        self.object.status = StatusTypes.WIP
        self.object.published = True
        candidates = self.object.get_responsible_candidates()
        if len(candidates) > 0:
            self.object.assigned = candidates[0]
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('office:issue', kwargs={'pk': self.object.pk})
