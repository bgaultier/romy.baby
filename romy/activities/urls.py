from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'activities'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:pk>/', login_required(views.BabyUpdateView.as_view()), name='baby_update'),
    path('<int:pk>/generate_apikey_view/', login_required(views.generate_api_key), name="generate_apikey"),
    path('activities/', login_required(views.ActivitiesListView.as_view()), name='list'),
    path('activities/bottle/create/', login_required(views.BottleActivityCreateView.as_view()), name='bottle_create'),
    path('activities/pee/create/', login_required(views.PeeActivityCreateView.as_view()), name='pee'),
    path('activities/pooh/create/', login_required(views.PoohActivityCreateView.as_view()), name='pooh'),
    path('activities/bath/create/', login_required(views.BathActivityCreateView.as_view()), name='bath'),
    path('activities/bottle/<int:pk>/', login_required(views.BottleActivityUpdateView.as_view()), name='bottle_update'),
    path('<int:pk>/activities.csv', login_required(views.activities_csv_view), name='csv_view'),
    path('activities/bottle/<int:pk>/', login_required(views.ActivityUpdateView.as_view()), name='update'),
    path('<int:pk>/activities/bottle/', views.bottle, name='bottle_api'),
    path('<int:pk>/activities/pee/', views.pee, name='pee_api'),
    path('<int:pk>/activities/pooh/', views.pooh, name='pooh_api'),
    path('<int:pk>/activities/bath/', views.bath, name='bath_api'),
    path('<int:baby_id>/activities/<int:pk>/delete/', login_required(views.ActivityDeleteView.as_view()), name='delete'),
]
