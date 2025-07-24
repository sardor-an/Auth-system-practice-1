from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.validators import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from .models import User, OneTimeUrl, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from shared.utility import send_email, link, uid64_decoder
from .serializer import UserSerializer, LoginRefreshSerializer
from .serializer import MySignUpSerializer, MyChangeUserInfoModelSerializer, MyChangeUserPhotoSerializer, MyLoginSerializer, MyLogoutSerializer, MyForgotPassword, MyForgotPasswordVerifySerializer, MyLoginRefreshSerializer, MyResetPasswordRebornSerializer


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
        user = serializer.validated_data['user']
        url = link(user)

        sent_link = f"http://127.0.0.1:8000/auth/password-reset/{url['uid64']}/{url['token']}"

        if serializer.validated_data['auth_type'] == VIA_EMAIL:
            send_email(serializer.validated_data['user'].email, sent_link)

        if serializer.validated_data['auth_type'] == VIA_PHONE:
            send_email(serializer.validated_data['user'].phone, sent_link)

        

        

        OneTimeUrl.objects.create(
                user=user,
                uid64=url['uid64'],
                token=url['token']
                
        )
        
        return Response({
            'success': True,
            'message': 'Verification url has been sent (demo)'
        })
class MyResetPasswordRebornApiView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request: Request, *args, **kwargs):
    
        serializer = MyResetPasswordRebornSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid64 = serializer.validated_data['uid64']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        user: User = uid64_decoder(uid64)
        url = user.one_time_urls.filter(is_used_once=False, token=token, uid64=uid64)
        
        if not url.exists():
            raise ValidationError({
                'msg': 'Url sucks'
            })
        
        url = url.first().delete()
        user.set_password(password)
        user.save()

        return Response({
            'message': 'Operation is done'
        })











class MyLoginRefreshApiView(APIView):
    permission_classes = [] # imagine your access is expired, how can you refresh it there is isAuthenticated
    
    def post(self, request: Request, *args, **kwargs):
        serializer = MyLoginRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            
            refresh_token = serializer.validated_data.get('refresh')
            refresh_obj = RefreshToken(refresh_token)
            refresh_obj.check_exp()
            user = get_object_or_404(User, id=refresh_obj['user_id'])

        except Exception as e:
            raise ValidationError({
                'success': False,
                'message': 'Something went wrong',
                'error': str(e)
            })

        
        refresh_obj.check_blacklist()
        refresh_obj.blacklist()
        new_refresh = RefreshToken.for_user(user)


        return Response({
            'success': True,
            'new_access': str(new_refresh.access_token),
            'new_refresh_token': str(new_refresh)

        })



    






class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer