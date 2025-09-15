# notes/models.py
from django.db import models
from django.utils.text import slugify

class Note(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(blank=True)   # markdown source
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # self-referential many-to-many for links (directed)
    links = models.ManyToManyField('self', symmetrical=False, related_name='linked_from', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "note"
            slug = base
            counter = 1
            while Note.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
