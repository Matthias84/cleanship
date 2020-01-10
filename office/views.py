from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from leaflet.forms.widgets import LeafletWidget

from common.models import Category, Issue, IssueFilter, StatusTypes, TrustTypes
from common.utils import send_author_email_notification
from .tables import IssueTable

@login_required
def start(request):
    l = []
    for g in request.user.groups.all():
        l.append(g.name)
    ourissues = Issue.objects.filter(assigned__in=request.user.groups.all())
    ouropenissues = ourissues.filter(status=StatusTypes.WIP)
    # all wip issues without review > 3d
    uncheckedIssues = ouropenissues.filter(published=False)
    checkdate = timezone.now()-timezone.timedelta(days=3)
    uncheckedIssues = uncheckedIssues.filter(created_at__lt=checkdate)
    # all wip issues without status update > 30d
    unupdatedIssues = ouropenissues.filter(published=True)
    checkdate = timezone.now()-timezone.timedelta(days=30)
    unupdatedIssues = unupdatedIssues.filter(status_created_at__lt=checkdate)
    # all wip ideas older > 60d
    catidee = Category.objects.filter(name='Idee').first()
    ourideas = ouropenissues.filter(category__in=catidee.get_descendants())
    return render(request, 'office/start.html', {'groups': l, 'issues3dunchecked': uncheckedIssues,'issues30dunupdated': unupdatedIssues, 'ideas60d': ourideas})

class IssueDetailView(LoginRequiredMixin, generic.DetailView):
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

class IssueListView(LoginRequiredMixin, SingleTableMixin, FilterView):
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

class IssueCreateView(LoginRequiredMixin, generic.CreateView):
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
        send_author_email_notification(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('office:issue', kwargs={'pk': self.object.pk})
