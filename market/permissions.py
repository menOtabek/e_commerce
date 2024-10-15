from rest_framework import status
from rest_framework.response import Response
from users.models import ADMIN, ORDINARY_USER
from exceptions.error_messages import ErrorCodes
from exceptions.exception import CustomAPIException


def is_super_admin(func):
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise CustomAPIException(ErrorCodes.FORBIDDEN)
        elif request.user.role == ADMIN:
            return func(self, request, *args, **kwargs)

        raise CustomAPIException(ErrorCodes.FORBIDDEN)

    return wrapper



def is_authenticated_user(func):
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise CustomAPIException(ErrorCodes.FORBIDDEN)
        elif request.user.role in [ADMIN, ORDINARY_USER]:
            return func(self, request, *args, **kwargs)
        raise CustomAPIException(ErrorCodes.FORBIDDEN)

    return wrapper