from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User

class UserUpdateView(generic.UpdateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email',)

    success_url = reverse_lazy('activities:index')
