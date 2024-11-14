from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import SignUpSerializer, UserSerializer
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(username=data['email']).exists():
            user = User.objects.create(
                first_name = data['first_name'],
                last_name = data['last_name'],
                email = data['email'],
                username = data['email'],
                password = make_password(data['password']),
            )
            return Response({ 'details': 'User Registered' }, status=status.HTTP_201_CREATED)

        else:
            return Response({ 'error': 'User already exists' }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):

    user = UserSerializer(request.user, many=False)
    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):

    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.username = data['email']
    user.email = data['email']

    if data['password'] != "":
        user.password = make_password(data['password'])
    user.save()
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)


@api_view(['POST'])
def forgot_password(request):
    try:
        data = request.data

        # Pobieranie użytkownika na podstawie email
        user = get_object_or_404(User, email=data['email'])

        # Generowanie tokenu i daty wygaśnięcia
        token = get_random_string(40)
        expire_date = timezone.now() + timedelta(minutes=300)

        # Zapisanie tokenu w profilu użytkownika
        user.profile.reset_password_token = token
        user.profile.reset_password_expire = expire_date
        user.profile.save()

        # Generowanie linku do resetu hasła
        host = get_current_host(request)  # Sprawdź, czy ta funkcja działa poprawnie
        link = "{host}api/reset_password/{token}".format(host=host, token=token)
        body = "Your password reset link is: {link}".format(link=link)

        # Wysyłanie maila
        send_mail(
            "Password reset for eShop",
            body,
            "noreply@eshop.com",
            [data['email']]
        )

        return Response({ 'details': 'Password reset email sent to: {email}'.format(email=data['email']) })

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def reset_password(request, token):
    data = request.data

    # Sprawdzenie, czy potrzebne dane są w żądaniu
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if password is None or confirm_password is None:
        return Response({'error': 'Both password fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Uzyskanie użytkownika
    user = get_object_or_404(User, profile__reset_password_token=token)

    # Sprawdzenie, czy token jest ważny
    if user.profile.reset_password_expire < timezone.now():
        return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)

    # Sprawdzenie, czy hasła są zgodne
    if password != confirm_password:
        return Response({'error': 'Passwords are not the same'}, status=status.HTTP_400_BAD_REQUEST)

    # Resetowanie hasła
    user.set_password(password)
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None

    user.profile.save()
    user.save()

    return Response({'details': 'Password reset successfully'}, status=status.HTTP_200_OK)


