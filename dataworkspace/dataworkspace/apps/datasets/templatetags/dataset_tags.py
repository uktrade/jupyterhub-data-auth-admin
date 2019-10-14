from django import template

register = template.Library()


@register.filter
def can_download_source(user, source):
    return source.user_has_download_access(user)
