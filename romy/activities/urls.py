from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'activities'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:pk>/', login_required(views.BabyUpdateView.as_view()), name='baby_update'),
    path('<int:pk>/generate_apikey_view/', login_required(views.generate_api_key), name="generate_apikey"),
    path('activities/', login_required(views.ActivitiesListView.as_view()), name='list'),
    path('analytics/bottles/', login_required(views.BottlesAnalyticsView.as_view()), name='bottles_analytics'),
    path('analytics/breastfeeding/', login_required(views.BreastFeedingAnalyticsView.as_view()), name='breastfeeding_analytics'),
    path('analytics/diapers/', login_required(views.DiaperAnalyticsView.as_view()), name='diapers_analytics'),
    path('analytics/baths/', login_required(views.BathsAnalyticsView.as_view()), name='baths_analytics'),
    path('activities/bottle/create/', login_required(views.BottleActivityCreateView.as_view()), name='bottle_create'),
    path('activities/pee/create/', login_required(views.PeeActivityCreateView.as_view()), name='pee'),
    path('activities/pooh/create/', login_required(views.PoohActivityCreateView.as_view()), name='pooh'),
    path('activities/bath/create/', login_required(views.BathActivityCreateView.as_view()), name='bath'),
    path('activities/breastfeeding/left/create/', login_required(views.BreastFeedingLeftActivityCreateView.as_view()), name='bf_l'),
    path('activities/breastfeeding/right/create/', login_required(views.BreastFeedingRightActivityCreateView.as_view()), name='bf_r'),
    path('activities/bottle/<int:pk>/', login_required(views.BottleActivityUpdateView.as_view()), name='bottle_update'),
    path('<int:pk>/activities.csv', login_required(views.activities_csv_view), name='csv_view'),
    path('<int:pk>/activities/', views.activities_api_view, name='api_view'),
    path('activities/<int:pk>/', login_required(views.ActivityUpdateView.as_view()), name='update'),
    path('<int:pk>/activities/bottle/', views.bottle, name='bottle_api'),
    path('<int:pk>/activities/pee/', views.pee, name='pee_api'),
    path('<int:pk>/activities/pooh/', views.pooh, name='pooh_api'),
    path('<int:pk>/activities/bath/', views.bath, name='bath_api'),
    path('<int:baby_id>/activities/<int:pk>/delete/', login_required(views.ActivityDeleteView.as_view()), name='delete'),
]
