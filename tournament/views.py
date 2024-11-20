
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .services import *
from .forms import ListPlayersForm


# Create your views here.
def setup(request):
    """View to set up tournament players."""
    if request.method == 'GET':
        form = get_prefilled_form()
        return render(request, 'tournament/setup.html', {'form': form})

    elif request.method == 'POST':
        form = ListPlayersForm(request.POST)
        if form.is_valid():
            get_or_create_tournament(setup=True)
            enroll_players(form.cleaned_data)
            return HttpResponseRedirect(reverse('tournament:start'))


@login_required
def start(request):
    """Starts the tournament view."""
    return render(request, "tournament/start.html")


@login_required
def play_round(request, n_round):
    """Plays a specified round, creating or retrieving matches as needed."""
    match_data, ranked_players, option_results = get_round_data(n_round)
    if n_round == 4:
        end_tournament()
        return JsonResponse({
            "ranked_players": ranked_players,
            "message": "The tournament has ended"
        })
    return JsonResponse(
        {
            "match_data": match_data,
            "ranked_players": ranked_players,
            "option_results": option_results
        },
    safe=False)


@login_required
def next_round(request):
    """Processes match results for the current round and updates player data."""
    if request.method == "POST":
        response_data = process_round_results(request)
        return JsonResponse(response_data, status=response_data.get("status_code", 200))


