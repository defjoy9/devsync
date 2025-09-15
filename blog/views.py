# blog/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wagtail.models import Page
from .forms import BlogPostForm
from .models import BlogPage, BlogIndexPage

@login_required
def create_post(request):
    # Find the blog index page to attach the new post under.
    # Prefer slug='blog' if you set it; fallback to first live BlogIndexPage.
    try:
        parent = BlogIndexPage.objects.live().get(slug='blog')
    except BlogIndexPage.DoesNotExist:
        parent = BlogIndexPage.objects.live().first()

    if parent is None:
        messages.error(request, "Blog index not found. Ask admin to create one.")
        return redirect('/')  # or some safe fallback

    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            intro = form.cleaned_data['intro']
            body = form.cleaned_data['body']
            publish_requested = form.cleaned_data.get('publish', False)

            # Only staff can publish immediately
            publish = publish_requested and request.user.is_staff

            # Create the page instance (do not set slug; add_child will handle it)
            new_page = BlogPage(
                title=title,
                intro=intro,
                body=body,
                author=request.user if request.user.is_authenticated else None
            )

            # Add the page as a child of the blog index
            parent.add_child(instance=new_page)

            # Save revision (and publish if allowed)
            revision = new_page.save_revision()
            if publish:
                revision.publish()
                messages.success(request, "Post created and published.")
                return redirect(new_page.url)
            else:
                # leave as draft
                messages.success(request, "Post created as draft. It will be visible after publishing.")
                return redirect(parent.url)
    else:
        form = BlogPostForm()

    return render(request, 'blog/create_post.html', {'form': form})
