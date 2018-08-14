from django.views import generic
from django.urls import reverse_lazy

from activities.models import BetaUser

class BetaUserCreateView(generic.CreateView):
    model = BetaUser
    fields = ('email',)
    template_name = 'coming-soon.html'

    success_url = reverse_lazy('activities:index')
