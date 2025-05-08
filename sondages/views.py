from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def dashboard (request):
    my_sondages = request.user.sondage_set.all()
    return render(request, 'sondages/dashboard.html', {'my_sondages': my_sondages})
