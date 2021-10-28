from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class HomePage(Page):
    # Database fields
    body = RichTextField(blank=True)

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full')
    ]

    # Parent page / subpage type rules
    parent_page_types = []
    subpage_types = ['news.NewsIndexPage', 'news.NewsTagIndexPage']
