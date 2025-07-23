from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import Base
from shared.utility import generate_code, generate_string
from datetime import datetime, timedelta

ORDINARY_USER, MANAGER, ADMIN = ('ORDINARY', 'MANAGER', 'ADMIN')
VIA_EMAIL, VIA_PHONE = ('VIA_EMAIL', 'VIA_PHONE')
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = ('NEW', 'CODE_VERIFIED', 'DONE', 'PHOTO_STEP')

PHONE_EXPIRATION_TIME = 2
EMAIL_EXPIRATION_TIME = 5


class User(AbstractUser, Base):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )

    AUTH_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    AUTH_STATUSES = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )

    user_role = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPES)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUSES, default=NEW)

    photo = models.ImageField(upload_to='user_photos', validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png'])])
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.EmailField(unique=True, null=True, blank=True)



    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def create_hash_password(self):
        if not self.password:
            self.password = generate_string()
            self.set_password(self.password)

    
    def create_confirmation(self, verify_type):
        code = generate_code()

        UserConfirmation(
            code=code,
            user_id=self.id,  # how does it work, there is no column called user_id
            verify_type=verify_type
        ).save()
        return code # actually it is needed but one case is ...
    
    def create_username(self):
        if not self.username:
            temp_username = f'instagram-user-{generate_string()}'
            while User.objects.filter(username=temp_username).exists():
                temp_username = f'instagram-user-{generate_string()}'
            self.username = temp_username

    def check_email_or_phone(self):
        if self.email:
            self.email = self.email.lower() # normalizing

        # there i will have encounter with "email already exists problem soon"


    def token(self):
        refresh = RefreshToken.for_user(self)
        token = {
            'access': str(refresh.access_token),
            'refresh_token': str(refresh)
        }
        return token

    def save(self, *args, **kwargs):
        self.create_username()
        self.create_hash_password()
        self.check_email_or_phone()
        super(User, self).save(*args, **kwargs)
class UserConfirmation(Base):

    TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_codes')
    verify_type = models.CharField(choices=TYPE_CHOICES, max_length=31)
    expiration_time = models.DateTimeField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s verification code"
    
    def save(self, *args, **kwargs):

        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)
        elif self.verify_type == VIA_PHONE:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRATION_TIME)

        super(UserConfirmation, self).save(*args, **kwargs)
class SmartToken(Base, models.Model):
    expiration_time = models.DateTimeField()
    token = models.CharField(max_length=255)
    is_confirmed = models.BooleanField(default=False)
    user = models.ForeignKey(related_name="smart_tokens", on_delete=models.CASCADE, to=User)

    def save(self, *args, **kwargs):
        if SmartToken.objects.filter(id=self.id).exists():
            current_user = SmartToken.objects.get(id=self.id)
            const_original = current_user.expiration_time
            if const_original != self.expiration_time:
                raise ValidationError('Expiration time cannot be changed')
        else:
            print('this line is working')
            self.expiration_time = datetime.now() + timedelta(minutes=2)
            
        
        super().save(*args, **kwargs)
class OneTimeTokenConfirmation(Base, models.Model):
    user = models.ForeignKey(to=User, related_name='one_time_token_confirmations', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_confirmed = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if OneTimeTokenConfirmation.objects.filter(id=self.id).exists():
            current_user = OneTimeTokenConfirmation.objects.get(id=self.id)
            const_original = current_user.expiration_time
            if const_original != self.expiration_time:
                raise ValidationError('Expiration time cannot be changed')
        else:
            print('this line is working')
            self.expiration_time = datetime.now() + timedelta(minutes=2)
            
        
        super().save(*args, **kwargs)