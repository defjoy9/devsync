from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

class BlogIndexPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        # get live child blog posts
        context['blogposts'] = self.get_descendants().live().specific()
        return context

class BlogPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField()
    content_panels = Page.content_panels + [FieldPanel('intro'), FieldPanel('body')]