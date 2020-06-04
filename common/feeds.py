from django.contrib.gis.feeds import Feed
from django.utils import feedgenerator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from common.models import Issue

class LatestIssueFeed(Feed):
    """
    Public feed listing all currently published issues
    """
    
    title = _('Cleanship issues')
    link = '/sitenews/'
    description = _('Updates on cleanship issues updates')
    
    def items(self):
        latestIssues = Issue.objects.filter(published=True)
        return latestIssues.order_by('-created_at')[:5]
    
    def item_pubdate(self, issue):
        return issue.created_at

    def item_title(self, issue):
        return issue.category
    
    def item_description(self, issue):
        return issue.description
    
    def item_geometry(self, issue):
        rsspos = issue.position
        rsspos.transform('WGS84')
        return rsspos

    def item_enclosures(self, issue):
        # Embedding photo
        if issue.photo:
            return [feedgenerator.Enclosure(issue.photo.url, str(issue.photo.size), 'image/{}'.format(issue.photo.name.split('.')[-1]))]

    # TODO: Add item_link for external frontend
    # TODO: Add more content, keywords etc. for clientside filtering

