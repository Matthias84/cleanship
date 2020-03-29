from django.conf import settings
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

from common.models import Category, Issue, StatusTypes, TrustTypes
from common.utils import send_author_email_notification
from .tables import IssueTable
from .filters import IssueFilter

@login_required
def start(request):
    l = []
    for g in request.user.groups.all():
        l.append(g.name)
    ourissues = Issue.objects.filter(assigned__in=request.user.groups.all())
    ouropenissues = ourissues.exclude(status__in=[StatusTypes.SOLVED, StatusTypes.IMPOSSIBLE, StatusTypes.DUBLICATE])
    # all review issues > 3d
    uncheckedIssues = ouropenissues.filter(status=StatusTypes.REVIEW)
    checkdate = timezone.now()-timezone.timedelta(days=3)
    uncheckedIssues = uncheckedIssues.filter(created_at__lt=checkdate)
    # all wip issues without status update > 30d
    unupdatedIssues = ouropenissues.filter(published=True)
    checkdate = timezone.now()-timezone.timedelta(days=30)
    unupdatedIssues = unupdatedIssues.filter(status_created_at__lt=checkdate)
    # all wip ideas older > 60d
    catidee = Category.get_ideas_root()
    if catidee:
        ourideas = ouropenissues.filter(category__in=catidee.get_descendants())
    else:
        ourideas = None
    return render(request, 'office/start.html', {'groups': l, 'issues3dunchecked': uncheckedIssues,'issues30dunupdated': unupdatedIssues, 'ideas60d': ourideas})

class IssueDetailView(LoginRequiredMixin, generic.DetailView):
    model = Issue
    template_name = 'office/issue.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = Issue.objects.filter(pk=self.kwargs.get('pk'))[0]
        trustMapping = {TrustTypes.INTERNAL: "internal", TrustTypes.EXTERNAL: "external", TrustTypes.FIELDTEAM: "fieldteam"}
        context['author_trust_string'] = trustMapping[issue.author_trust]
        statusMapping = {StatusTypes.SUBMITTED: "submitted",
                        StatusTypes.REVIEW: "review",
                        StatusTypes.WIP: "wip",
                        StatusTypes.SOLVED: "solved",
                        StatusTypes.IMPOSSIBLE: "impossible",
                        StatusTypes.DUBLICATE: "dublicate"}
        context['status_string'] = statusMapping[issue.status]
        positionWidget = issue.position
        positionWidget.transform(settings.EPSG_WIDGET)
        positionWidget = positionWidget.geojson
        context['position_geojson'] = positionWidget
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
            positionWidget = issue.position
            positionWidget.transform(settings.EPSG_WIDGET)
            issue.position_webmap = positionWidget.geojson
        return context

class IssueCreateView(LoginRequiredMixin, generic.CreateView):
    model = Issue
    fields = ['description', 'category', 'author_email', 'position','photo']
    template_name = 'office/issue_create.html'
    
    def get_form(self):
        form = super(IssueCreateView, self).get_form()
        form.fields['position'].widget = LeafletWidget()
        form.fields['author_email'].help_text = 'eMail of subitter (usually a citizen, will get a info mail. No confirmation nessesary)'
        form.fields['position'].help_text = 'Try to map the position as accurate as possible (used to determine landowner and location description)'
        form.fields['photo'].help_text = 'Photo showing the spot and surroundings'
        return form
        
    def get_initial(self):
        initial = super(IssueCreateView, self).get_initial()
        initial = initial.copy()
        initial['author_email'] = self.request.user.email
        return initial
    
    def form_valid(self, form):
        # Set issue defaults if submitted via office users
        self.object = form.save(commit=False)
        self.object.status = StatusTypes.REVIEW
        self.object.published = False
        candidates = self.object.get_responsible_candidates()
        if len(candidates) > 0:
            self.object.assigned = candidates[0]
        self.object.save()
        send_author_email_notification(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('office:issue', kwargs={'pk': self.object.pk})
