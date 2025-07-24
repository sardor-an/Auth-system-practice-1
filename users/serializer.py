from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import NotFound
from django.core.validators import FileExtensionValidator
from django.contrib.auth.password_validation import validate_password
from .models import User, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, PHOTO_STEP, NEW
from shared.utility import identify_auth_type, send_email, name_checker, success_false

class MySignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )

        extra_kwargs = {
            'id': {'read_only': True, 'required': False},
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
        }

    def __init__(self, instance=None, data=..., **kwargs):
        super(MySignUpSerializer, self).__init__(instance, data, **kwargs)
        self.fields['email_phone'] = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email_phone = data.get('email_phone')


        if identify_auth_type(email_phone) == 'email':
            data = {
                'email': email_phone,
                'auth_type': VIA_EMAIL
            }
        elif identify_auth_type(email_phone) == 'phone':
            data = {
                'phone': email_phone,
                'auth_type': VIA_PHONE
            }
        
        else:
            raise ValidationError({
                'success': False,
                'message':'Neither, email nor phone'
            })
        return data
    
    def create(self, validated_data):
        new_user: User =  super(MySignUpSerializer, self).create(validated_data)
        
        if new_user.auth_type == VIA_EMAIL:
            code = new_user.create_confirmation(VIA_EMAIL)
            send_email(validated_data.get('email'), code)
        elif new_user.auth_type == VIA_PHONE:
            code = new_user.create_confirmation(VIA_PHONE)
            send_email(validated_data.get('phone'), code)
        new_user.save()

        return new_user
    def to_representation(self, instance: User):
        data = super().to_representation(instance)
        token_pair = instance.token()
        data.update(token_pair)
        return data
class MyChangeUserInfoModelSerializer(serializers.Serializer):
    
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    def update(self, instance: User, validated_data):
        print(validated_data)
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.username = validated_data['username']
        instance.auth_status = DONE
        instance.set_password(validated_data['password'])
        instance.save()

        return instance

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if password and confirm_password:
            if password != confirm_password:
                success_false('Passwords do not match')

            validate_password(password)
            validate_password(confirm_password)

        return data


    def validate_username(self, value):
        if not name_checker(value, username=True):
            success_false('Username is invalid')
        

        return value
    def validate_first_name(self, value):
        
        if not name_checker(value):
            raise ValidationError({
                'success': False,
                'message': 'Firstname is invalid'
            })
        
        return value
    def validate_last_name(self, value):
        
        if not name_checker(value):
            raise ValidationError({
                'success': False,
                'message': 'Lastname is invalid'
            })
        
        return value
class MyChangeUserPhotoSerializer(serializers.Serializer):

    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png',])], required=True)

    def update(self, instance: User, validated_data):
        if self.fields['photo']:
            instance.photo = validated_data.get('photo')
            instance.auth_status = PHOTO_STEP
            instance.save()

        return instance
class MyLoginSerializer(TokenObtainPairSerializer):
    email_phone = serializers.CharField(write_only=True, required=True)
    def __init__(self, instance=None, data=..., **kwargs):
        super(MyLoginSerializer, self).__init__(instance, data, **kwargs)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def get_user(self, **kwargs):
        user = User.objects.filter(**kwargs)
        if not user.exists():
            raise NotFound({
                'success': False,
                'message': 'User not found'
            })
        return user

    def auth_validate(self, data: dict):
        email_phone = data.get('email_phone')
        
        auth_type = identify_auth_type(email_phone)

        if auth_type == 'email':
            user = self.get_user(email=email_phone)
        elif auth_type == 'phone':
            user = self.get_user(phone=email_phone)
        else:
            raise success_false('Neither, email nor phone, please enter the valid format')
        
        
        auth_kwargs = {
            self.username_field: user.first().username,
            'password': data.get('password')
        }


        if user.first() and user.first().auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError({
                'success': False,
                'message': 'You have not completed registering yet'
            })
        
        user = authenticate(**auth_kwargs)

        if not user:
            raise ValidationError({
                'success':False,
                'message': 'Login or password is wrong'
            })
        self.user = user
        return data

    def validate(self, attrs):
        self.auth_validate(attrs)

        attrs = self.user.token()
        attrs['auth_status'] = self.user.auth_status

        return attrs
class MyLoginRefreshSerializer(serializers.Serializer): # TokenrefreshSer
    refresh = serializers.CharField(required=True, write_only=True)
class MyLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)
class MyForgotPassword(serializers.Serializer):
    email_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email_phone = data.get('email_phone', None)

        auth_type = identify_auth_type(email_phone)

        if auth_type == 'email':
            user = self.get_user(email=email_phone)
            data['auth_type'] = VIA_EMAIL

        elif auth_type == 'phone':
            user = self.get_user(phone=email_phone)
            data['auth_type'] = VIA_PHONE

        else:
            raise ValidationError({
                'success': False,
                'message': 'Neither, email or phone'
            })
        data['user'] = user
        return data


    def get_user(self, **kwargs):
        user = User.objects.filter(**kwargs)

        if not user.exists():
            raise NotFound({
                "success": False,
                "message": 'User not found'
            })
        
        return user.first()
class MyForgotPasswordVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True, write_only=True)
class MyResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)


    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        validate_password(password)
        validate_password(password_confirm)

        if password_confirm != password:
            raise ValidationError({
                'success': False,
                'message': 'Password do not match (demo)'
            })
        
        return data
    
    def update(self, instance: User, validated_data):
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class MyResetPasswordRebornSerializer(serializers.Serializer):
    uid64 = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)


    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        validate_password(password)
        validate_password(password_confirm)

        if password_confirm != password:
            raise ValidationError({
                'success':True,
                'message': 'Password do not match'
            })
        
        return data


class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data
