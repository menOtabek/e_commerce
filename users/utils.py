import re
import threading
from twilio.rest import Client
from .models import User, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from exceptions.error_messages import ErrorCodes
from exceptions.exception import CustomAPIException
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from decouple import config
from datetime import datetime
email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
phone_regex = re.compile(r"(^\+998([- ])?(90|91|93|94|95|98|99|33|97|71)([- ])?(\d{3})([- ])?(\d{2})([- ])?(\d{2})$)")
username_regex = re.compile(r"\b[A-Za-z0-9._-]{3,}\b")


def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = "email"

    elif re.fullmatch(phone_regex, email_or_phone):
        email_or_phone = "phone"
    else:
        raise CustomAPIException(ErrorCodes.VALIDATION_FAILED)
    return email_or_phone


def check_user_type(user_input):
    if re.fullmatch(username_regex, user_input):
        user_input = "username"
    elif re.fullmatch(phone_regex, user_input):
        user_input = "phone"
    elif re.fullmatch(email_regex, user_input):
        user_input = "email"
    else:
        raise CustomAPIException(ErrorCodes.VALIDATION_FAILED)
    return user_input


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']],
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'code': code}
    )
    Email.send_email(
        {
            'subject': "Registration",
            'to_email': email,
            'body': html_content,
            'content_type': 'html'
        }
    )


def send_phone_code(phone, code):
    account_sit = config('account_sit')
    auth_token = config('auth_token')
    client = Client(account_sit, auth_token)
    client.messages.create(
        body="Hi, your confirmation code is {}\n".format(code),
        from_="+998938340103",
        to=f"{phone}"
    )
    

def verify(self, request):
        user = request.user
        code = request.data.get('verify_code')
        check_verify(user, code)
        result = {
            'auth_status': user.auth_status,
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token'],
        }
        return result

def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            raise CustomAPIException(ErrorCodes.EXPIRED_OR_INVALID_CODE)
        verifies.update(is_confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


def get_verify_code(self, request):
        user = request.user
        check_verification(user)
        if user.auth_types == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_types == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED)
        return {'message': 'Your verification code sent again!'}


def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            raise CustomAPIException(ErrorCodes.NOT_EXPIRED)
