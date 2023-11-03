import jwt
from rest_framework import permissions

from .models import User
from rocketData.settings import SECRET_KEY


class IsActivate(permissions.BasePermission):

    def has_permission(self, request, view):
        access = False
        try:
            token = request.headers.get('Authorization').split(' ')[1]
            user_id = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]).get('user_id')
            if User.objects.get(id=user_id).is_active == True:
                access = True
                return True
        except AttributeError:
            pass
        print(access)
        return access





