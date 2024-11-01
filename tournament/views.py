from django.http import HttpResponse
from django.shortcuts import render

from .forms import ListPlayersForm

# Create your views here.
def setup(request):
    if request.method == 'POST':
        form = ListPlayersForm(request.POST)

        if form.is_valid():
            return HttpResponse('<h3>Success!</h3>')

    elif request.method == 'GET':
        form = ListPlayersForm()
    return render(request, "tournament/setup.html", {"form": form})


