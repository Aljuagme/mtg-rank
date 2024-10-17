from sqlite3 import IntegrityError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.urls import reverse


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "mtg/index.html", {
            "user": request.user
        })
    else:
        return HttpResponseRedirect(reverse("mtg:login"))


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("mtg:index"))
        else:
            return render(request, "mtg/login.html", {
                "message": "Invalid credentials."
            })
    else:
        return render(request, "mtg/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("mtg:index"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "mtg/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError:
            return render(request, "mtg/register.html", {
                "message": "User with that email already exists."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("mtg:index"))
    else:
        return render(request, "mtg/register.html")