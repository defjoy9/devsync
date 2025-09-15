# blog/models.py
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
class BlogIndexPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        # get live child blog posts
        context['blogposts'] = self.get_descendants().live().specific()
        return context

class BlogPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField()
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts'
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('author')
    ]

    def serve(self, request):
        from .forms import BlogCommentForm  # import inside to avoid circular import
        context = self.get_context(request)
        context['comment_form'] = BlogCommentForm()

        if request.method == 'POST':
            form = BlogCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.blog_post = self
                if request.user.is_authenticated:
                    comment.user = request.user
                comment.save()
                return redirect(self.url)

        return render(request, "blog/blog_page.html", context)

class BlogComment(models.Model):
    blog_post = models.ForeignKey(BlogPage, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog_post.title}"