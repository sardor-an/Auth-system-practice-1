from random import randint, choices
from re import match
from uuid import uuid4
from rest_framework.exceptions import NotFound, ValidationError
import phonenumbers # for the future

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model



def uid64_decoder(uid64):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uid64))  
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise ValidationError({
            'WARNING': 'SERVER GOT FUCKED'
        })

    return user




def link(user):
    uid64 = urlsafe_base64_encode(force_bytes(str(user.pk)))
    token = PasswordResetTokenGenerator().make_token(user)
    
    return {
        'uid64': uid64,
        'token': token }





email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
phone_pattern = r'^\+?\d{7,15}$'  # Accepts digits with optional '+' sign, 7-15 digits
name_pattern = r"^(?=.{5,30}$)[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?$"
username_pattern = r"^(?!.*[._]{2})(?!.*[._]$)[a-z][a-z0-9._]{4,29}$"


def check_user_type(value: str) -> str:
    if match(email_pattern, value):
        return 'email'
    elif match(phone_pattern, value):
        return 'phone'
    elif match(username_pattern, value):
        return 'username'
    else:
        raise NotFound({
            'success': False,
            'message': 'Invalid'
        })

def success_false(message):
    raise ValidationError({
        'success': False,
        'message': message
    })


def send_email(email, code):
    print(code)

def generate_string():
    temp_str = ''.join(choices(str(uuid4()).split('-'), k=randint(0, 4)))
    return temp_str


def generate_code():
    code = ''.join([str(randint(0,1000) % 10) for _ in range(0, 6)])
    return code

def identify_auth_type(value: str) -> str:
    

    if match(email_pattern, value):
        return 'email'
    elif match(phone_pattern, value):
        return 'phone'
    else:
        return None
    
def name_checker(value: str, username = False):
    
    if not username:
        return match(name_pattern, value)
    
    return match(username_pattern, value)
    