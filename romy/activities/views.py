from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Sum

from datetime import timedelta

import csv

from .models import Baby, Activity


class IndexView(generic.ListView):
    model = Activity
    template_name = 'index.html'

    def get_queryset(self):
        babies = Baby.objects.filter(parent=self.request.user)
        return babies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = self.get_queryset()
        babies_list = []
        for baby in babies:
            activities = Activity.objects.filter(baby=baby)
            night_activities = Activity.objects.filter(baby=baby, created_date__hour__lt=8, created_date__gt=timezone.now().replace(hour=0, minute=0))
            bottles_today = activities.filter(type='BOTTLE', created_date__gt=timezone.now().replace(hour=0, minute=0))
            night_bottles = bottles_today.filter(created_date__hour__lt=8)
            day_bottles = len(bottles_today) - len(night_bottles)
            diapers_today = activities.filter(type__startswith='P', created_date__gt=timezone.now().replace(hour=0, minute=0))
            night_diapers = diapers_today.filter(created_date__hour__lt=8)
            day_diapers = len(diapers_today) - len(night_diapers)
            bath = activities.filter(type='BATH', created_date__gt=timezone.now().replace(hour=0, minute=0))
            try:
                next_bottle = bottles_today.first().created_date + timedelta(minutes=baby.feeding_period)
            except AttributeError:
                next_bottle = None

            try:
                last_diaper = diapers_today.first().created_date
            except AttributeError:
                last_diaper = None

            try:
                last_bath = activities.filter(type='BATH').first().created_date
            except AttributeError:
                last_bath = None

            bottles = []
            for d in range(6, -1, -1):
                dt = timezone.now() - timedelta(days=d)
                bottles.append(activities.filter(type='BOTTLE', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year).annotate(total_amount=Sum('quantity')))

            diapers = []
            for d in range(6, -1, -1):
                dt = timezone.now() - timedelta(days=d)
                diapers.append(activities.filter(type__startswith='P', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year))

            baths = []
            for d in range(3, -1, -1):
                dt = timezone.now() - timedelta(days=d)
                bath = activities.filter(type='BATH', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year)
                if bath:
                    baths.append(bath.first().created_date)
                else:
                    baths.append(dt.replace(hour=0, minute=0))

            babies_list.append({
                'first_name':baby.first_name,
                'id':baby.id,
                'activities':activities.filter(created_date__gt=timezone.now().replace(hour=0, minute=0)),
                'night_activities':night_activities,
                'bottles': {
                    'today':bottles_today,
                    'night':night_bottles,
                    'day':day_bottles,
                    'next':next_bottle,
                    'week':bottles,
                },
                'diapers': {
                    'today':diapers_today,
                    'night':night_diapers,
                    'day':day_diapers,
                    'last':last_diaper,
                    'week': diapers,
                },
                'bath': {
                    'today':bath,
                    'last':last_bath,
                    'last_days':baths,
                },
            })
        context['babies'] = babies_list
        return context

def generate_api_key(request, pk):
    baby=get_object_or_404(Baby, parent=request.user,  pk=pk)
    baby.generate_api_key()
    baby.save()

    return HttpResponseRedirect('/babies/' + str(baby.id))

class BabyUpdateView(generic.UpdateView):
    model = Baby
    success_url = reverse_lazy('activities:index')
    fields = ('first_name', 'feeding_period')

class ActivityDeleteView(generic.DeleteView):
    model = Activity
    success_url = reverse_lazy('activities:index')

    def get_queryset(self):
        baby = get_object_or_404(Baby, parent=self.request.user)
        qs = super(ActivityDeleteView, self).get_queryset()
        return qs.filter(baby=baby)

class ActivitiesListView(generic.ListView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = Baby.objects.filter(parent=self.request.user)
        babies_list = []
        for baby in babies:
            activities = Activity.objects.filter(baby=baby)
            night_activities = Activity.objects.filter(baby=baby, created_date__hour__lt=8)
            babies_list.append({
                'first_name':baby.first_name,
                'id':baby.id,
                'activities':activities[:100],
            })
        context['babies'] = babies_list
        return context

@csrf_exempt
def activities_api_view(request, pk):
    baby = get_object_or_404(Baby, pk=pk, api_key=request.GET.get('key'))
    activities = Activity.objects.filter(baby=baby)
    bottles_today = activities.filter(type='BOTTLE', created_date__gt=timezone.now().replace(hour=0, minute=0))
    diapers_today = activities.filter(type__startswith='P', created_date__gt=timezone.now().replace(hour=0, minute=0))
    bath = activities.filter(type='BATH', created_date__gt=timezone.now().replace(hour=0, minute=0))
    try:
        next_bottle = bottles_today.first().created_date + timedelta(minutes=baby.feeding_period)
        next_bottle = next_bottle.astimezone(timezone.get_current_timezone())
    except AttributeError:
        next_bottle = None
    response={
        'id':baby.id,
        'first_name':baby.first_name,
        'activities':len(activities.filter(created_date__gt=timezone.now().replace(hour=0, minute=0))),
        'bottles': {
            'today':len(bottles_today),
            'next':next_bottle,
            'next_time':next_bottle.strftime("%H:%M")
        },
        'diapers':len(diapers_today),
        'bath':len(bath)
    }
    return JsonResponse(response)

def activities_csv_view(request, pk):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activities.csv"'

    baby = get_object_or_404(Baby, pk=pk, parent=request.user)
    activities = Activity.objects.filter(baby=baby)

    writer = csv.writer(response)

    writer.writerow(['timestamp', 'type', 'quantity', 'comment', 'last_connection'])
    for activity in activities:
        writer.writerow([activity.created_date, activity.type,  activity.quantity, activity.comment,  activity.last_connection ])

    return response

class BottleActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('quantity', 'comment')
    success_url = reverse_lazy('activities:index')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, parent=self.request.user)
        form.instance.baby = baby
        form.instance.created_date = timezone.now()
        form.instance.type = 'BOTTLE'
        return super().form_valid(form)

class BottleActivityUpdateView(generic.UpdateView):
    model = Activity
    fields = ('quantity', 'comment', 'created_date')
    success_url = reverse_lazy('activities:index')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, parent=self.request.user)
        return super().form_valid(form)

class ActivityUpdateView(generic.UpdateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:index')

class PeeActivityCreateView(generic.CreateView):
    model = Activity
    fields = ['comment']
    success_url = reverse_lazy('activities:index')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, parent=self.request.user)
        form.instance.baby = baby
        form.instance.created_date = timezone.now()
        form.instance.type = 'PEE'
        return super().form_valid(form)

class PoohActivityCreateView(generic.CreateView):
    model = Activity
    fields = ['comment']
    success_url = reverse_lazy('activities:index')

    def form_valid(self, form):
        print(self)
        baby = get_object_or_404(Baby, parent=self.request.user)
        form.instance.baby = baby
        form.instance.created_date = timezone.now()
        form.instance.type = 'POOH'
        return super().form_valid(form)

class BathActivityCreateView(generic.CreateView):
    model = Activity
    fields = ['comment']
    success_url = reverse_lazy('activities:index')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, parent=self.request.user)
        form.instance.baby = baby
        form.instance.created_date = timezone.now()
        form.instance.type = 'BATH'
        return super().form_valid(form)

@csrf_exempt
def bottle(request, pk):
    baby = get_object_or_404(Baby, pk=pk, api_key=request.GET.get('key'))
    activity = Activity(baby=baby, created_date=timezone.now(), type='BOTTLE')
    activity.last_connection = request.META.get("REMOTE_ADDR", "")
    activity.save()

    activities = Activity.objects.filter(baby=baby)
    bottles_today = activities.filter(type='BOTTLE', created_date__gt=timezone.now().replace(hour=0, minute=0))
    night_bottles = bottles_today.filter(created_date__hour__lt=8)
    day_bottles = len(bottles_today) - len(night_bottles)
    try:
        next_bottle = bottles_today.first().created_date + timedelta(minutes=baby.feeding_period)
    except AttributeError:
        next_bottle = None
    return JsonResponse({
        'baby':baby.first_name,
        'bottles': {
            'today':len(bottles_today),
            'night':len(night_bottles),
            'day':day_bottles,
            'next':next_bottle,
        },
    })

@csrf_exempt
def pee(request, pk):
    baby = get_object_or_404(Baby, pk=pk, api_key=request.GET.get('key'))
    activity = Activity(baby=baby, created_date=timezone.now(), type='PEE')
    activity.last_connection = request.META.get("REMOTE_ADDR", "")
    activity.save()

    activities = Activity.objects.filter(baby=baby)
    diapers_today = activities.filter(type__startswith='P', created_date__gt=timezone.now().replace(hour=0, minute=0))
    night_diapers = diapers_today.filter(created_date__hour__lt=8)
    day_diapers = len(diapers_today) - len(night_diapers)
    try:
        last_diaper = diapers_today.first().created_date
    except AttributeError:
        last_diaper = None
    return JsonResponse({
        'baby':baby.first_name,
        'diapers': {
            'today':diapers_today,
            'night':night_diapers,
            'day':day_diapers,
            'last':last_diaper,
        }
    })

@csrf_exempt
def pooh(request, pk):
    baby = get_object_or_404(Baby, pk=pk, api_key=request.GET.get('key'))
    activity = Activity(baby=baby, created_date=timezone.now(), type='POOH')
    activity.last_connection = request.META.get("REMOTE_ADDR", "")
    activity.save()

    activities = Activity.objects.filter(baby=baby)
    diapers_today = activities.filter(type__startswith='P', created_date__gt=timezone.now().replace(hour=0, minute=0))
    night_diapers = diapers_today.filter(created_date__hour__lt=8)
    day_diapers = len(diapers_today) - len(night_diapers)
    try:
        last_diaper = diapers_today.first().created_date
    except AttributeError:
        last_diaper = None
    return JsonResponse({
        'baby':baby.first_name,
        'diapers': {
            'today':diapers_today,
            'night':night_diapers,
            'day':day_diapers,
            'last':last_diaper,
        }
    })

@csrf_exempt
def bath(request, pk):
    baby = get_object_or_404(Baby, pk=pk, api_key=request.GET.get('key'))
    activity = Activity(baby=baby, created_date=timezone.now(), type='BATH')
    activity.last_connection = request.META.get("REMOTE_ADDR", "")
    activity.save()

    return JsonResponse({'baby':baby.first_name})
