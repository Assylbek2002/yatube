from django.http import HttpResponseRedirect


def user_only(func):
    def check_user(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(
                redirect_to="/auth/login",
            )
        func(request, *args, **kwargs)

    return check_user
