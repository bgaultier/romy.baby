from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from activities.models import BetaUser

class BetaUserCreateView(generic.CreateView):
    model = BetaUser
    fields = ('email',)
    template_name = 'coming-soon.html'
    success_url = reverse_lazy('coming_soon')

    def form_valid(self, form):
        messages.success(self.request, _(u"Votre demande de création de compte a bien été enregistrée, vous recevrez prochainement vos identifiants par email !"))
        return super().form_valid(form)

class UserUpdateView(generic.UpdateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email',)

    success_url = reverse_lazy('activities:index')
