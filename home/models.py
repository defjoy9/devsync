from django.db import models
from django.shortcuts import render
from wagtail.models import Page

class HomePage(Page):
    def serve(self, request):
        if not request.user.is_authenticated:
            template = "home/welcome_page.html"
        else:
            template = "home/home_page.html"
        return render(request, template, self.get_context(request))
