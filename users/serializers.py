from pyexpat.errors import messages

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import check_password

from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import serializers
from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied
from .utils import check_email_or_phone, send_email, check_user_type
from exceptions.error_messages import ErrorCodes
from exceptions.exception import CustomAPIException


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    # add new field don't use model, using __init__
    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    # auth_type = serializers.CharField(read_only=True, required=False)    # equal to extra_kwargs line 35
    # aut_status = serializers.CharField(read_only=True, required=False)   # equal to extra_kwargs line 36
    class Meta:
        model = User
        fields = (
            'id',
            'auth_types',
            'auth_status',
        )

        extra_kwargs = {
            'auth_types': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_types == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_types == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            # send_phone_code(user.phone_number, code)
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_types': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_types': VIA_PHONE
            }
        else:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED)
        return data

    @staticmethod
    def validate_email_phone_number(value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            raise CustomAPIException(ErrorCodes.USER_ALREADY_EXISTS)
        elif value and User.objects.filter(phone_number=value).exists():
            raise CustomAPIException(ErrorCodes.USER_ALREADY_EXISTS)
        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class CodeVerifyRequestSerializer(serializers.Serializer):
    verify_code = serializers.IntegerField(required=True)


class CodeVerifyResponseSerializer(serializers.Serializer):
    auth_status = serializers.CharField()
    access = serializers.CharField()
    refresh = serializers.CharField()


class ChangeUserInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise CustomAPIExceptin(ErrorCodes.INVALID_INPUT)
        if password and confirm_password:
            validate_password(password)
            validate_password(confirm_password)
        return data

    def validate_username(self, username):
        if len(username) < 3 or len(username) > 64:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message='Username name must be between 3 and 64 characters')
        if not username.isalpha:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, messages='Username can not be entirely numeric')
        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 3 or len(first_name) > 64:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message='First name must be between 3 and 64 characters')
        if not first_name.isalpha():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message='First name must contain only alphabetic characters')
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 3 or len(last_name) > 64:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message='Last name must be between 3 and 64 characters')
        if not last_name.isalpha():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message='Last name must contain only alphabetic characters')
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class PartialChangeUserInformation(ChangeUserInformationSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['user_input'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(read_only=True, required=False)

    def auth_validate(self, data):
        user_input = str(data.get('user_input')).lower()
        print(user_input, '*' * 20)
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED)
        password = data.get('password', '')
        current_user = User.objects.filter(username__iexact=username).first()
        print(current_user, '*' * 20)
        print(current_user.auth_status, '*' * 20)
        if current_user is not None and current_user.auth_status in [CODE_VERIFIED, NEW]:
            raise CustomAPIException(ErrorCodes.NOT_REGISTERED_YET)
        print(current_user.password, '*' * 20)

        if check_password(password, current_user.password):
            self.user = current_user

        else:
            raise CustomAPIException(ErrorCodes.INVALID_INPUT)

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_STEP]:
            raise CustomAPIException(ErrorCodes.FORBIDDEN)
        data = self.user.token()
        print(data, 'token  ' * 10)
        data['auth_status'] = self.user.auth_status
        data['role'] = self.user.user_roles
        print(data, 'token  ' * 10)
        return data

    @staticmethod
    def get_user(**kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise CustomAPIException(ErrorCodes.USER_DOES_NOT_EXISTS)
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token = AccessToken(data.get('access'))
        user_id = access_token['user_id']
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise CustomAPIException(ErrorCodes.USER_DOES_NOT_EXISTS)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        if not email_or_phone:
            raise CustomAPIException(ErrorCodes.INVALID_INPUT)
        user = User.objects.filter(Q(email=email_or_phone) | Q(phone_number=email_or_phone))
        if not user:
            raise CustomAPIException(ErrorCodes.USER_DOES_NOT_EXISTS)
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'password', 'confirm_password')

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise CustomAPIException(ErrorCodes.INVALID_INPUT)
        if password:
            validate_password(password)
            return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        instance.save()
        return instance
        # return super(ResetPasswordSerializer, self).update(instance, validated_data)  # password update qilinyapti
