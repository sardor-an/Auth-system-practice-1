from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.validators import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.timezone import now
from .models import User, SmartToken, OneTimeTokenConfirmation, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from shared.utility import send_email, generate_code

from .serializer import UserSerializer
from .serializer import MySignUpSerializer, MyChangeUserInfoModelSerializer, MyChangeUserPhotoSerializer, MyLoginSerializer, MyLogoutSerializer, MyForgotPassword, MyForgotPasswordVerifySerializer, MyResetPasswordSerializer

class MySignUpView(CreateAPIView):
    serializer_class = MySignUpSerializer
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
class MyChangeUserInfoApiView(APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['put', 'patch']

    def put(self, request: Request, *args, **kwargs):
        serializer = MyChangeUserInfoModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=request.user, validated_data=serializer.validated_data)

        user_serializer = UserSerializer(instance=request.user)
        

        data = {
            'success': True,
            'messgae': f'Complete changes have been saved for user {request.user}',
            'user': user_serializer.data
        }

        return Response(data)
    
    def patch(self, request: Request, *args, **kwargs):
        serializer = MyChangeUserInfoModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=request.user, validated_data=serializer.validated_data)

        user_serializer = UserSerializer(instance=request.user)
        

        data = {
            'success': True,
            'messgae': f'Partial changes have been saved for user {request.user}',
            'user': user_serializer.data
        }

        return Response(data)
class MychangeUserInfoApiUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['put', 'patch']
    serializer_class = MyChangeUserInfoModelSerializer


    def get_object(self):
        return self.request.user
class MychanegUserPhotoApiView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.all()
    serializer_class = MyChangeUserPhotoSerializer
    http_method_names = ['put', 'patch']

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, instance=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': 'Image has been uploaded successfully'
        })
    def get_object(self):
        return self.request
class MyResendCodeApiView(APIView):
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request: Request, *args, **kwargs):
        user: User = request.user
        user_verifies = user.verified_codes.filter(is_confirmed=False, expiration_time__gte=now())
        if user.auth_status != NEW:
            raise ValidationError({
                'success': False,
                'message': 'This user cannot get new code because user has been already verified',
                'auth_status': user.auth_status
            })
        if user_verifies.exists():
            raise ValidationError({
                'success': False,
                'message': 'You have active codes, please wait and try again'
            })
        
        code = user.create_confirmation(user.auth_type)
        if user.auth_type == VIA_EMAIL:
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            # send_phone(user.phone, code)
            send_email(user.phone, code)
        
        token_pair = user.token()
        return Response({
            'success': True,
            'message': 'New verification code has been sent',
            'access': token_pair['access'],
            'refresh_token': token_pair['refresh_token'],
        })
class MyVerifyApiView(APIView):
    permission_classes = [IsAuthenticated, ]
    


    def check_verify(self, user: User, code):


        if user.auth_status != NEW:
            raise ValidationError({
                'success': False,
                'message': 'You have already registered',
                'auth_status': user.auth_status
            })

        code_confirmation = user.verified_codes.filter(is_confirmed=False, code=code, expiration_time__gte=now())
        

        if code_confirmation.exists():
            code_confirmation.update(is_confirmed=True)
            user.auth_status = CODE_VERIFIED
            user.save()

            return user
        else:
            raise ValidationError({
                'success':False,
                'message': 'Code you entered might be wrong or expired'
            })
        

    def post(self, request: Request, *args, **kwargs):
        code = request.data.get('code', None)
        user: User = request.user
        if code is None:
            raise ValidationError({
                'success': False,
                'message': 'Enter the verification code, because this field is required'
            })
        self.check_verify(user, code)

        user_serializer = UserSerializer(instance=user)
        token_pair = user.token()
        data = {
            'success': True,
            'message': 'You registered successfully',
            'access': token_pair['access'],
            'refresh_token': token_pair['refresh_token'],
            'user': user_serializer.data
        }

        return Response(data)
class MyLoginApiView(TokenObtainPairView):
    serializer_class = MyLoginSerializer
class MyLogutApiView(APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post']
    serializer_class = MyLogoutSerializer
    

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = request.data.get('refresh')

            refresh_obj = RefreshToken(refresh_token)
            if refresh_obj['user_id'] != request.user.id:
                raise ValidationError(detail={
                    'success': True,
                    'message': 'Refresh token does not belong to requested user'
                })
            
            refresh_obj.check_blacklist()

            refresh_obj.blacklist()

            return Response({
                'success': True,
                'message': 'You logged out successfully'
            })
    
        
        except Exception as e:
            return Response({
                'success': False,
                'message':e.detail
            })
class MyForgotPasswordApiView(APIView):
    permission_classes = [AllowAny, ]
    
    def post(self, request: Request, *args, **kwargs):
        serializer = MyForgotPassword(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = generate_code()
        if serializer.validated_data['auth_type'] == VIA_EMAIL:
            send_email(serializer.validated_data['user'].email, code)

        if serializer.validated_data['auth_type'] == VIA_PHONE:
            send_email(serializer.validated_data['user'].phone, code)

        OneTimeTokenConfirmation.objects.create(
                user=serializer.validated_data['user'],
                code=str(code)
            )
        
        return Response({
            'success': True,
            'message': 'Verification code has been sent (demo)',
            'access': serializer.validated_data['user'].token()['access']
        })
class MyForgotPasswordVerifyApiView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = MyForgotPasswordVerifySerializer

    def post(self, request: Request, *args, **kwargs):
        code = request.data.get('code', None)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        otc_instance = request.user.one_time_token_confirmations.filter(user_id=self.request.user.pk, code=code, expiration_time__gte=now(), is_confirmed=False)

        if not otc_instance.exists():
            raise ValidationError({
                'success':False, 
                'message': 'Your code is expired or wrong'
            })
        one_time_token = request.user.token()['refresh_token']
        SmartToken(user=request.user, token=one_time_token).save()

        return Response({
            'warning': 'PLEASE HURRY UP, TOKEN LIVES FOR ONLY 2 MINUTES',
            'success': True,
            'message': 'Your one time token that for changing password has been created successfully',
            'one_time_token': one_time_token
        })
class MyResetPasswordApiView(APIView):
    permission_classes = [AllowAny, ]

    def put(self, request: Request, *args, **kwargs):
        print(request.headers)
        one_time_token = request.headers.get('One-Time-Token', None)
        serializer = MyResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if one_time_token is None:
            raise ValidationError({
                'success': False, 
                'message': 'one_time_token must be given in headers'
            })
        
        
        one_time_token_instance = request.user.smart_tokens.filter(user_id=request.user.pk, is_confirmed=False, expiration_time__gte=now(), token=one_time_token)
        
        if not one_time_token_instance.exists():
            raise ValidationError({
                'success':False,
                'message': 'Smart token not found'
            })
        
        serializer.update(request.user, serializer.validated_data)
        used_token = RefreshToken(one_time_token)
        used_token.blacklist()
        one_time_token_instance.first().delete()

        return Response({
            'success': True,
            'message': 'Password has been changed successfully (demo)'
        })