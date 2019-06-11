"""romy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .views import UserUpdateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="coming-soon.html"), name='coming_soon'),
    path('signup/', CreateView.as_view(template_name='registration/signup.html',
                                       form_class=UserCreationForm,
                                       success_url='/babies/'), name='signup'),
    path('admin/', admin.site.urls),
    path('babies/', include('activities.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/<int:pk>/', login_required(UserUpdateView.as_view()), name='update_user'),
]
