from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def start(request):
    l = []
    for g in request.user.groups.all():
        l.append(g.name)
    return render(request, 'office/start.html', {'groups': l})
