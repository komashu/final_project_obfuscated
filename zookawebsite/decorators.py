
def get_user(function):
    def username(request):
        u = request.user.username
        uid = u.split("@")[0]
        return uid