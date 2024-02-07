from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.html import conditional_escape
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
def timesince(date_time: datetime, autoescape=True):
    '''Return Custom Time'''
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    if date_time and isinstance(date_time, datetime):
        now = timezone.now()
        time_delta = max(now - date_time, timedelta(seconds=0))
        time_since = ''
        if time_delta <= timedelta(minutes=1):
            time_since = 'Just Now'
        elif time_delta <= timedelta(days=2) and (now.date().day - date_time.date().day) == 1:
            time_since = 'Yesterday'
        elif time_delta > timedelta(minutes=1) and time_delta < timedelta(days=1):
            time_since = date_time.strftime('%H:%M')
        elif time_delta >= timedelta(days=1) and time_delta < timedelta(days=7):
            time_since = date_time.strftime('%a %d')
        elif time_delta >= timedelta(days=7) and time_delta < timedelta(days=365):
            time_since = date_time.strftime('%d %b')
        elif time_delta >= timedelta(days=365):
            time_since = date_time.strftime('%d %b %Y')
        return mark_safe(time_since)
    return mark_safe(date_time)

