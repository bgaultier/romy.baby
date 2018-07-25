from django.shortcuts import render

from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Baby, Activity


class IndexView(generic.ListView):
    model = Activity
    template_name = 'index.html'

    def get_queryset(self):
        baby = get_object_or_404(Baby, parent=self.request.user)
        return baby
