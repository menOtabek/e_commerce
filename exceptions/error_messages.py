from rest_framework import status
from enum import Enum


class ErrorCodes(Enum):
    UNAUTHORIZED = 1
    INVALID_INPUT = 2
    FORBIDDEN = 3
    NOT_FOUND = 4
    ALREADY_EXISTS = 5
    USER_ALREADY_EXISTS = 6
    USER_DOES_NOT_EXISTS = 7
    INCORRECT_PASSWORD = 8
    INVALID_TOKEN = 9
    EXPIRED_TOKEN = 10
    VALIDATION_FAILED = 11
    EXPIRED_OR_INVALID_CODE = 12
    NOT_EXPIRED = 13
    NOT_REGISTERED_YET = 14


error_messages = {
    1: {'result': 'Unauthorized access', 'status_code': status.HTTP_401_UNAUTHORIZED},
    2: {'result': 'Invalid input provided', 'status_code': status.HTTP_400_BAD_REQUEST},
    3: {'result': 'Permission denied', 'status_code': status.HTTP_403_FORBIDDEN},
    4: {'result': 'Resource does not exist', 'status_code': status.HTTP_404_NOT_FOUND},
    5: {'result': 'Resource already exists', 'status_code': status.HTTP_409_CONFLICT},
    6: {'result': 'User already exists', 'status_code': status.HTTP_409_CONFLICT},
    7: {'result': 'User does not exist', 'status_code': status.HTTP_404_NOT_FOUND},
    8: {'result': 'Incorrect password provided', 'status_code': status.HTTP_400_BAD_REQUEST},
    9: {'result': 'Incorrect token provided', 'status_code': status.HTTP_400_BAD_REQUEST},
    10: {'result': 'Token expired', 'status_code': status.HTTP_400_BAD_REQUEST},
    11: {'result': 'Validation failed', 'status_code': status.HTTP_400_BAD_REQUEST},
    12: {'result': 'Your confirmation code is invalid or expired', 'status_code': status.HTTP_400_BAD_REQUEST},
    13: {'result': 'Your confirmation code is not expired', 'status_code': status.HTTP_400_BAD_REQUEST},
    14: {'result': 'You have not fully registered yet', 'status_code': status.HTTP_400_BAD_REQUEST},
}


def get_error_message(code):
    return error_messages.get(code, 'Unknown error')
