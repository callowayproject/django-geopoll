"""
The data models for polls, choices and votes
"""
import datetime

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db.models import permalink
from django.http import Http404
from django.conf import settings as django_settings

from settings import MULTIPLE_SITES, USER_MODEL, MONTH_FORMAT

if MULTIPLE_SITES:
    from django.contrib.sites.models import Site

COMMENT_STATUSES = (
    (1, _('Comments Enabled')),
    (0, _('Comments Disabled')),
    (2, _('Comments Frozen'))
)

class PollExpired(Exception):
    """
    The poll has expired
    """
    pass

class GeoPollMetadata(models.Model):
    """
    Simple Key-Value Store
    """
    key = models.CharField(blank=True, max_length=255)
    value = models.CharField(blank=True, max_length=255)
    
    class Meta:
        pass

    def __unicode__(self):
        return u"GeoPollMetadata"

class GeoPollManager(models.GeoManager):
    """
    Adds some basic utility functions for the Poll objects as a whole
    """
    def get_latest_polls(self, count=10, include_expired=False):
        """
        Return the latest <count> polls, optionally including the expired polls
        """
        queryset = super(GeoPollManager, self).get_query_set()
        params = {
            'start_date__lt': datetime.datetime.now()
        }
        if MULTIPLE_SITES:
            params['sites__pk'] = django_settings.SITE_ID

        if include_expired:
            args = []
        else:
            from django.db.models import Q
            args = [
                Q(expire_date__isnull=True) |
                Q(expire_date__gt=datetime.datetime.now()) 
            ]
        
        polls = queryset.filter(*args, **params).order_by('-start_date')
        
        return polls[:count]


class GeoPoll(models.Model):
    """
    The basic model for a poll. It includes the question and how it should
    expire (by date, or manually)
    """
    question = models.CharField(max_length=255)
    slug = models.SlugField()
    if MULTIPLE_SITES:
        sites = models.ManyToManyField(Site, 
            related_name="geopolls")
    start_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, null=True)
    total_votes = models.IntegerField(editable=False, default=0)
    comment_status = models.IntegerField(
        'Comments', 
        default=0, 
        choices=COMMENT_STATUSES)
    metadata = models.ManyToManyField(GeoMetadata)
    
    objects = GeoPollManager()
    
    class Meta:
        ordering = ('-start_date',)
    
    def __unicode__(self):
        return self.question
    
    @permalink
    def get_absolute_url(self):
        """
        The absolute url for this poll
        """
        return ('geopoll_detail', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime(MONTH_FORMAT).lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    @permalink
    def get_absolute_results_url(self):
        """
        The absolute url for the results of this poll
        """
        from django.core.urlresolvers import reverse
        return ('geopoll_results', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime(MONTH_FORMAT).lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    @permalink
    def get_absolute_comments_url(self):
        """
        The absolute url for comments of this poll
        """
        return ('geopoll_comments', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime(MONTH_FORMAT).lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    def is_expired(self):
        """
        Check if the poll has expired. This is True if there is no expire date, 
        or the expire date has not occured
        """
        if self.expire_date is None:
            return False
        elif self.expire_date <= datetime.datetime.now():
            return True
    
    def vote(self, choice, user, source, addr_str, latitude=None, longitude=None):
        """
        Vote on a poll.
        
        Does all the checks for duplication
        
        :param choice:       The id, or :class:`GeoPollChoice` voted
        :type choice:        int or :class:`GeoPollChoice`
        :param user:         The user who voted.
        :type user:          A Django USER_MODEL instance
        :param str source:   Where the vote came from
        :param str addr_str: The address string entered by the user for geocoding
        :param float latitude: The latitude of a previously geocoded address
        :param float longitude: The longitude of a previously geocoded address
        """
        if self.is_expired():
            raise PollExpired()
        
        try:
            if isinstance(choice, GeoPollChoice):
                selected_choice = choice
            else:
                selected_choice = GeoPollChoice.objects.get(pk=choice)
        except PollChoice.DoesNotExist:
            raise Http404("Selected choice does not exist")
        
        if bool(latitude and longitude):
            latlong = Point(longitude, latitude)
        else:
            latlong = None
        
        GeoVote.objects.create(
            poll=self, 
            choice=selected_choice, 
            user=user,
            source=source,
            addr_str=addr_str,
            latlong=latlong)
        
        selected_choice.votes += 1
        selected_choice.save()
        self.total_votes += 1
        self.save()


class GeoPollChoice(models.Model):
    """
    Choices for polls. Choices are referenced by their own unique id for voting.
    """
    poll = models.ForeignKey(GeoPoll)
    choice = models.CharField(max_length=255)
    votes = models.IntegerField(editable=False, default=0)
    order = models.IntegerField(default=1)
    metadata = models.ManyToManyField(GeoMetadata)
    
    def percentage(self):
        """
        The percentage of the total votes in the poll that choce this option
        """
        total = self.poll.total_votes
        if total == 0 or self.votes == 0:
            return 0
        return int((float(self.votes) / float(total)) * 100)
    
    def __unicode__(self):
        return self.choice
        
    class Meta:
        ordering = ['order',]

class GeoVote(models.Model):
    """
    A User's vote on a poll
    """
    poll = models.ForeignKey(GeoPoll, related_name="votes")
    choice = models.ForeignKey(GeoPollChoice)
    user = models.ForeignKey(USER_MODEL)
    source = models.CharField(blank=True, max_length=255)
    addr_str = models.CharField(blank=True, max_length=255)
    latlong = models.PointField()
    metadata = models.ManyToManyField(GeoMetadata)
    
    class Meta:
        unique_together = ('choice', 'user')
