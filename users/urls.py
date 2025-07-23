from django.urls import path
from .views import MySignUpView, MyVerifyApiView, MyChangeUserInfoApiView, MychangeUserInfoApiUpdateView, \
    MychanegUserPhotoApiView, MyResendCodeApiView, MyLoginApiView, MyLogutApiView, \
    MyForgotPasswordApiView,MyForgotPasswordVerifyApiView, MyResetPasswordApiView

urlpatterns = [ 


    # genius
    path('gen/forgot-password/', MyForgotPasswordApiView.as_view()),
    path('gen/forgot-password-verify/', MyForgotPasswordVerifyApiView.as_view()),
    path('gen/reset-password/', MyResetPasswordApiView.as_view()),


    # hard practice 1
    path('mine/logout/', MyLogutApiView.as_view()),
    path('mine/login/', MyLoginApiView.as_view()),
    path('mine/resend-code/', MyResendCodeApiView.as_view()),
    path('mine/changeuserphoto/', MychanegUserPhotoApiView.as_view()),
    path('mine/changeuserinfoupdate/', MychangeUserInfoApiUpdateView.as_view()),
    path('mine/changeuserinfo/', MyChangeUserInfoApiView.as_view()),
    path('mine/verify-code/', MyVerifyApiView.as_view()),
    path('mine/signup/', MySignUpView.as_view())
]