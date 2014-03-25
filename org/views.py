from annoying.decorators import render_to
from agreement.models import Agreement
from django.shortcuts import redirect
from django.contrib import auth

from django.http import HttpResponseRedirect

@render_to('login.html')
def login(request):
    if request.method != 'POST':
        return {}

    invalid = False

    org_code = request.POST.get('org_code')
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = auth.authenticate(org_code=org_code, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        next = request.GET.get('next')
        if next:
            return HttpResponseRedirect(next)

        return HttpResponseRedirect(reverse('index'))

    ctx = dict(
        org_code=org_code,
        username=username
    )
    return ctx



def logout(request):
    auth.logout(request)
    return redirect('login')
