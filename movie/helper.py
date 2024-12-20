from .models import CustomUser
from django.contrib.auth.hashers import check_password

def authenticate(username=None, password=None):
    try:
        # Get the corresponding user.
        user = CustomUser.objects.get(username=username)
        #  If password, matches just return the user. Otherwise, return None.
        if check_password(password, user.password):
            return user
        return None
    except CustomUser.DoesNotExist:
        # No user was found.
        return None