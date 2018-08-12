from django.http import HttpResponse
from django.template import loader

def coming_soon(request):
    template = loader.get_template('coming-soon.html')
    context = {}
    return HttpResponse(template.render(context, request))
