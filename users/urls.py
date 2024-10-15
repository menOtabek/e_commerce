from django.urls import path
from .views import (SignUpApiView, VerifyApiView, NewVerifyCodeApiView,
                    ChangeUserInformationApiView, ChangeUserPhotoApiView, LoginApiView, LoginApiView, LogoutApiView,
                    ForgotPasswordApiView, ResetPasswordApiViewSet)

urlpatterns = [
    path('login/', LoginApiView.as_view({'post': 'login'}), name='login'),
    path('login/refresh/', LoginApiView.as_view({'post': 'refresh'}), name='login_refresh'),
    path('logout/', LogoutApiView.as_view({'post': 'logout'}), name='logout'),
    path('signup/', SignUpApiView.as_view({'post': 'create'}), name='signup'),
    path('verify-code/', VerifyApiView.as_view({'post': 'verify_code'}), name='verify_code'),
    path('new-verify-code/', NewVerifyCodeApiView.as_view({'get': 'get_new_code'}), name='new_verify_code'),
    path('change-user-information/', ChangeUserInformationApiView.as_view({'put': 'update', 'patch': 'partial_update'}), name='change-user-information'),
    path('change-user-photo/', ChangeUserPhotoApiView.as_view({'put': 'update'}), name='change-user-photo'),
    path('forgot-password/', ForgotPasswordApiView.as_view({'post': 'forgot_password'}), name='forgot-password'),
    path('reset-password/', ResetPasswordApiViewSet.as_view({'post': 'reset_password'}), name='reset-password'),
]
