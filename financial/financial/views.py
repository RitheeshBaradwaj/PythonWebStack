from django.http import HttpResponse


def health_check(request):
    return HttpResponse("Service is up and running")
