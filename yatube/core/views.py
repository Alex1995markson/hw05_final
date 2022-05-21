# core/views.py
from django.shortcuts import render, render_to_response
from django.template import RequestContext


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def server_error(request, *args, **argv):
    response = render_to_response('core/500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response
