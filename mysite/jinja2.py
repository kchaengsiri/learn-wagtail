from django.templatetags.static import static
from django.urls import reverse

from wagtail.core.templatetags.wagtailcore_tags import wagtail_site
from jinja2 import Environment, contextfunction


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'wagtail_site': contextfunction(wagtail_site)
    })
    return env
