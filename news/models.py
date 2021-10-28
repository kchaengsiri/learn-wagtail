from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core import blocks
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class NewsIndexPage(Page):
    # Database fields
    intro = RichTextField(blank=True)

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full')
    ]

    # Parent page / subpage type rules
    parent_page_types = ['home.HomePage']
    subpage_types = ['news.NewsPage']

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        newspages = self.get_children().live().order_by('-first_published_at')
        context['newspages'] = newspages
        return context

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'


class NewsPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'NewsPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class NewsPage(Page):
    # Database fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    # body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=NewsPageTag, blank=True)
    categories = ParentalManyToManyField('news.NewsCategory', blank=True)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])
    # use_only_image_template = models.BooleanField()

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="News information"),
        FieldPanel('date'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
        # FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Gallery images"),
        InlinePanel('related_links', label="Related links"),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['NewsIndexPage']
    subpage_types = []

    # ajax_template = 'flash_news.html'
    # template = 'custom_news_page.html'

    @property
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    # def get_template(self, request):
    #     if self.use_only_image_template:
    #         return 'news/only_image_news_page.html'
    #     return 'news/news_page.html'

    class Meta:
        verbose_name = 'News article'
        verbose_name_plural = 'News article'


class NewsPageRelatedLink(Orderable):
    page = ParentalKey(NewsPage, on_delete=models.CASCADE,
                       related_name='related_links')
    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
    ]


class NewsPageGalleryImage(Orderable):
    page = ParentalKey(
        NewsPage,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class NewsTagIndexPage(Page):

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        newspages = NewsPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['newspages'] = newspages
        return context

    class Meta:
        verbose_name = 'News tag'
        verbose_name_plural = 'News tag'


@register_snippet
class NewsCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'News category'
        verbose_name_plural = 'News categories'
