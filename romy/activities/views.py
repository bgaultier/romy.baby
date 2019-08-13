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

from .models import Baby, Activity, BetaUser

class BetaUserCreateView(generic.CreateView):
    model = BetaUser
    fields = ('email')
    template_name = 'coming-soon.html'

    success_url = reverse_lazy('activities:index')

class IndexView(generic.ListView):
    model = Activity
    template_name = 'index.html'

    def get_queryset(self):
        babies = Baby.objects.filter(parents=self.request.user)
        if babies.count() < 1:
            baby = Baby(first_name="Bébé")
            baby.save()
            baby.parents.add(self.request.user)
            baby.save()
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
                bottles_by_day = activities.filter(type='BOTTLE', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year)
                amount = bottles_by_day.aggregate(Sum('quantity'))
                bottles.append({'datetime':dt, 'amount': amount})

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
    baby=get_object_or_404(Baby, parents=request.user, pk=pk)
    baby.generate_api_key()
    baby.save()

    return HttpResponseRedirect('/babies/' + str(baby.id))

class BabyUpdateView(generic.UpdateView):
    model = Baby
    success_url = reverse_lazy('activities:index')
    fields = ('first_name', 'feeding_period')

    def get_queryset(self):
        baby = get_object_or_404(Baby, pk=self.kwargs['pk'], parents=self.request.user)
        queryset = super(BabyUpdateView, self).get_queryset()
        return queryset.filter(id=baby.id)

class ActivityDeleteView(generic.DeleteView):
    model = Activity
    success_url = reverse_lazy('activities:index')

    def get_queryset(self):
        baby = get_object_or_404(Baby, pk=self.kwargs['baby_id'], parents=self.request.user)
        queryset = super(ActivityDeleteView, self).get_queryset()
        return queryset.filter(baby=baby)

class ActivitiesListView(generic.ListView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = Baby.objects.filter(parents=self.request.user)
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

    baby = get_object_or_404(Baby, pk=pk, parents=request.user)
    activities = Activity.objects.filter(baby=baby)

    writer = csv.writer(response)

    writer.writerow(['timestamp', 'type', 'quantity', 'comment', 'last_connection'])
    for activity in activities:
        writer.writerow([activity.created_date, activity.type,  activity.quantity, activity.comment,  activity.last_connection ])

    return response

class BottleActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('quantity', 'comment', 'created_date')
    success_url = reverse_lazy('activities:list')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, pk=self.request.POST.get('baby_id'), parents=self.request.user)
        form.instance.baby = baby
        if not form.instance.created_date:
            form.instance.created_date = timezone.now()
        form.instance.type = 'BOTTLE'
        form.instance.parent = self.request.user
        return super().form_valid(form)

class BottleActivityUpdateView(generic.UpdateView):
    model = Activity
    fields = ('quantity', 'comment', 'created_date')
    success_url = reverse_lazy('activities:list')

class ActivityUpdateView(generic.UpdateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:list')

class PeeActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:list')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, pk=self.request.POST.get('baby_id'), parents=self.request.user)
        form.instance.baby = baby
        if not form.instance.created_date:
            form.instance.created_date = timezone.now()
        form.instance.type = 'PEE'
        form.instance.parent = self.request.user
        return super().form_valid(form)

class PoohActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:list')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, pk=self.request.POST.get('baby_id'), parents=self.request.user)
        form.instance.baby = baby
        if not form.instance.created_date:
            form.instance.created_date = timezone.now()
        form.instance.type = 'POOH'
        form.instance.parent = self.request.user
        return super().form_valid(form)

class BathActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:list')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, pk=self.request.POST.get('baby_id'), parents=self.request.user)
        form.instance.baby = baby
        if not form.instance.created_date:
            form.instance.created_date = timezone.now()
        form.instance.type = 'BATH'
        form.instance.parent = self.request.user
        return super().form_valid(form)

class BreastFeedingLeftActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:list')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, pk=self.request.POST.get('baby_id'), parents=self.request.user)
        form.instance.baby = baby
        if not form.instance.created_date:
            form.instance.created_date = timezone.now()
        form.instance.type = 'BF_L'
        form.instance.parent = self.request.user
        return super().form_valid(form)

class BreastFeedingRightActivityCreateView(generic.CreateView):
    model = Activity
    fields = ('comment', 'created_date')
    success_url = reverse_lazy('activities:list')

    def form_valid(self, form):
        baby = get_object_or_404(Baby, pk=self.request.POST.get('baby_id'), parents=self.request.user)
        form.instance.baby = baby
        if not form.instance.created_date:
            form.instance.created_date = timezone.now()
        form.instance.type = 'BF_R'
        form.instance.parent = self.request.user
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
            'today':diapers_today.count(),
            'night':night_diapers.count(),
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
            'today':diapers_today.count(),
            'night':night_diapers.count(),
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


class BottlesAnalyticsView(generic.ListView):
    model = Activity
    template_name = 'activities/bottles.html'

    def get_queryset(self):
        babies = Baby.objects.filter(parents=self.request.user)
        return babies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = self.get_queryset()
        babies_list = []
        for baby in babies:
            activities = Activity.objects.filter(baby=baby)

            last_month_bottles = []
            last_2_weeks_bottles = []
            total_amount = 0
            total_bottles = 0
            my_bottles = 0
            for d in range(31, 14, -1):
                dt = timezone.now() - timedelta(days=d)
                bottles_by_day = activities.filter(type='BOTTLE', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year)
                amount = bottles_by_day.aggregate(Sum('quantity'))
                last_month_bottles.append({'datetime':dt, 'amount': amount})

            smart_bottles = 0
            smart_bottle_amount = 0
            smart_bottle_total_amount = 0
            for d in range(14, -1, -1):
                dt = timezone.now() - timedelta(days=d)
                bottles_by_day = activities.filter(type='BOTTLE', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year)
                amount = bottles_by_day.aggregate(Sum('quantity'))
                if amount.get('quantity__sum'):
                    total_amount += amount.get('quantity__sum')
                if bottles_by_day:
                    total_bottles += bottles_by_day.count()
                my_bottles += len(bottles_by_day.filter(parent=self.request.user))

                bottles_within_2_hours = bottles_by_day.filter(created_date__hour__lt=timezone.now().hour+1, created_date__hour__gt=timezone.now().hour-1)
                smart_bottle_amount = bottles_within_2_hours.aggregate(Sum('quantity'))
                if smart_bottle_amount.get('quantity__sum'):
                    smart_bottle_total_amount += smart_bottle_amount.get('quantity__sum')
                    smart_bottles += 1

                last_month_bottles.append({'datetime':dt, 'amount': amount})
                last_2_weeks_bottles.append({'datetime':dt, 'amount': amount})

            smart_bottle = 0
            if smart_bottles > 0:
                smart_bottle = smart_bottle_total_amount/smart_bottles + 30
                smart_bottle = smart_bottle+30 - smart_bottle%30

            babies_list.append({
                'first_name':baby.first_name,
                'id':baby.id,
                'last_month_bottles': last_month_bottles,
                'last_2_weeks_bottles': last_2_weeks_bottles,
                'bottles_average_quantity': total_amount/len(last_2_weeks_bottles),
                'bottles_average': total_bottles/15,
                'smart_bottle': smart_bottle,
                'my_bottles_percentage': int(my_bottles*100/total_bottles),
            })
        context['babies'] = babies_list

        return context

class BreastFeedingAnalyticsView(generic.ListView):
    model = Activity
    template_name = 'activities/breastfeeding.html'

    def get_queryset(self):
        babies = Baby.objects.filter(parents=self.request.user)
        return babies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = self.get_queryset()
        babies_list = []
        for baby in babies:
            activities = Activity.objects.filter(baby=baby)

            last_month = timezone.now() - timedelta(days=30)
            last_month_left_feedings = activities.filter(type='BF_L', created_date__gt=last_month).count()
            last_month_right_feedings = activities.filter(type='BF_R', created_date__gt=last_month).count()

            today_left_feedings = activities.filter(type='BF_L', created_date__gt=timezone.now().replace(hour=0, minute=0)).count()
            today_right_feedings = activities.filter(type='BF_L', created_date__gt=timezone.now().replace(hour=0, minute=0)).count()

            babies_list.append({
                'first_name':baby.first_name,
                'id':baby.id,
                'last_month_left_feedings': last_month_left_feedings,
                'last_month_right_feedings': last_month_right_feedings,
                'today_left_feedings': today_left_feedings,
                'today_right_feedings': today_right_feedings,
            })
        context['babies'] = babies_list

        return context

class DiaperAnalyticsView(generic.ListView):
    model = Activity
    template_name = 'activities/diapers.html'

    def get_queryset(self):
        babies = Baby.objects.filter(parents=self.request.user)
        return babies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = self.get_queryset()
        babies_list = []
        for baby in babies:
            activities = Activity.objects.filter(baby=baby)

            diapers = []
            total_amount = 0
            total_diapers = 0
            my_diapers = 0
            for d in range(31, -1, -1):
                dt = timezone.now() - timedelta(days=d)
                diapers_by_day = activities.filter(type__startswith='P', created_date__day=dt.day, created_date__month=dt.month, created_date__year=dt.year)
                amount = len(diapers_by_day)
                if diapers_by_day:
                    total_diapers += amount
                my_diapers += len(diapers_by_day.filter(parent=self.request.user))
                diapers.append({'datetime':dt, 'amount': amount})

            babies_list.append({
                'first_name':baby.first_name,
                'id':baby.id,
                'diapers':diapers,
                'total_diapers':total_diapers,
                'diapers_average': total_diapers/31,
                'my_diapers_percentage': int(my_diapers*100/total_diapers),
            })
        context['babies'] = babies_list

        return context

class BathsAnalyticsView(generic.ListView):
    model = Activity
    template_name = 'activities/baths.html'

    def get_queryset(self):
        babies = Baby.objects.filter(parents=self.request.user)
        return babies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        babies = self.get_queryset()
        babies_list = []
        for baby in babies:
            baths = Activity.objects.filter(baby=baby, type='BATH')

            babies_list.append({
                'first_name':baby.first_name,
                'id':baby.id,
                'baths':baths,
            })
        context['babies'] = babies_list

        return context
