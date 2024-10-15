from rest_framework.viewsets import ViewSet
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from exceptions.error_messages import ErrorCodes
from exceptions.exception import CustomAPIException
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import send_email, check_email_or_phone, verify, get_verify_code
from .serializers import (SignUpSerializer, ChangeUserInformationSerializer, ChangeUserPhotoSerializer,
                          LoginSerializer, LoginRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer,
                          ResetPasswordSerializer, PartialChangeUserInformation,
                          CodeVerifyRequestSerializer, CodeVerifyResponseSerializer)
from .models import User, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE


class SignUpApiView(ViewSet):
    permission_classes = [permissions.AllowAny, ]

    @swagger_auto_schema(
        operation_summary='Sign Up',
        operation_description='Sign up for your account',
        request_body=SignUpSerializer,
        responses={201: SignUpSerializer()},
        tags=['Authentication'],
    )
    def create(self, request):
        serializer = SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_201_CREATED)


class VerifyApiView(ViewSet):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_summary='Verify Confirmation Code',
        operation_description='Verify the user confirmation code provided by the user.',
        request_body=CodeVerifyRequestSerializer,
        responses={201: CodeVerifyResponseSerializer()},
        tags=['Authentication'],
    )
    def verify_code(self, request):
        result = verify(self, request)
        return Response(data={'result': result, 'ok': True}, status=status.HTTP_200_OK)


class NewVerifyCodeApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='New Verify Confirmation Code',
        operation_description='New Verify the user confirmation code provided by the user.',
        responses={201: CodeVerifyResponseSerializer()},
        tags=['Authentication'],
    )
    def get_new_code(self, request):
        result = get_verify_code(self, request)
        return Response(data={'result': result, 'ok': True}, status=status.HTTP_200_OK)


class ChangeUserInformationApiView(ViewSet):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_summary='Update User Information',
        operation_description='Update the authenticated user information.',
        request_body=ChangeUserInformationSerializer,
        responses={200: ChangeUserInformationSerializer()},
        tags=['Authentication'], )
    def update(self, request):
        serializer = ChangeUserInformationSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        user = request.user
        serializer.update(user, serializer.validated_data)
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Partially Update User Information',
        operation_description='Partially update the authenticated user information.',
        request_body=PartialChangeUserInformation,
        responses={200: PartialChangeUserInformation()},
        tags=['Authentication'], )
    def partial_update(self, request):
        serializer = PartialChangeUserInformation(data=request.data, partial=True)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        user = request.user
        serializer.update(user, serializer.validated_data)
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)


class ChangeUserPhotoApiView(ViewSet):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_summary='Update User Photo Information',
        operation_description='Update the authenticated user information.',
        request_body=ChangeUserPhotoSerializer,
        responses={200: ChangeUserPhotoSerializer()},
        tags=['Authentication'],
    )
    def update(self, request):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        user = self.request.user
        serializer.update(user, serializer.validated_data)
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)


class LoginApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='Login',
        operation_description='Login a user.',
        request_body=LoginSerializer,
        responses={200: openapi.Response('Login successful',
                                         openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                             'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                             'access': openapi.Schema(type=openapi.TYPE_STRING), }))},
        tags=['Authentication'],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Login refresh',
        operation_description='Login refresh a user.',
        request_body=LoginRefreshSerializer,
        responses={200: openapi.Response('Login successful',
                                         openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                             'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                             'access': openapi.Schema(type=openapi.TYPE_STRING), }))},
        tags=['Authentication'],
    )
    def refresh(self, request):
        serializer = LoginRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        return Response(data={'result': serializer.validated_data, 'ok': True}, status=status.HTTP_200_OK)


class LogoutApiView(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Logout',
        operation_description='Logout a user.',
        request_body=LogoutSerializer,
        responses={200: openapi.Response('Logout successful', )},
        tags=['Authentication'],
    )
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(data={'result': 'Logged out successfully', 'ok': True},
                        status=status.HTTP_205_RESET_CONTENT
                        )


class ForgotPasswordApiView(ViewSet):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(
        operation_summary='Forgot Password',
        operation_description='Forget password.',
        request_body=ForgotPasswordSerializer,
        responses={200: openapi.Response('Send code and tokens', )},
        tags=['Authentication'],
    )
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone, code)
        elif check_email_or_phone(email_or_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)
        data = {'message': 'Your confirmation code sent again!',
                'access': user.token()['access'],
                'refresh': user.token()['refresh_token'],
                'user_status': user.auth_status, }
        return Response(data={'result': data, 'ok': True}, status=status.HTTP_200_OK)


class ResetPasswordApiViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Reset Password',
        operation_description='Reset password.',
        request_body=ResetPasswordSerializer,
        responses={200: openapi.Response('Password reset successfully', )},
        tags=['Authentication']
    )
    def reset_password(self, request):
        user = request.user
        serializer = ResetPasswordSerializer(user, data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        serializer.save()
        data = {
            'message': 'Password reset successfully',
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token'],
        }
        return Response(data={'result': data, 'ok': True}, status=status.HTTP_200_OK)
