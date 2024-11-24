from .models import User


def process_login(request):
    name_or_email = request.POST["name_or_email"]
    password = request.POST["password"]

    try:
        user = User.objects.get(username=name_or_email.capitalize())
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=name_or_email)
        except User.DoesNotExist:
            user = None
    finally:
        return user, password