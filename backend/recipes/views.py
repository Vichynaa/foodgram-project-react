from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from .models import Recipe, Tag, Ingredient
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from foodgram.settings import ADMIN_EMAIL
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer, ObtainTokenSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


def send_confirmation_code(user):
    '''Отправка кода подверждения в email'''
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Код подтверждения в API'
    message = f'{confirmation_code} - Код для поддверждения авторизации в API'
    admin_email = ADMIN_EMAIL
    user_email = [user.email]
    send_mail(subject, message, admin_email, user_email)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    '''Регистрация нового пользователя'''
    email = request.data.get('email')
    username = request.data.get('username')

    if (User.objects.filter(Q(email=email)).exists()
            and not User.objects.filter(Q(username=username)).exists()):
        return Response(
            {'message': 'Пользователь с таким email уже зарегистрирован'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(Q(username=username) & ~Q(email=email)).exists():
        return Response(
            {'message': 'Пользователь с таким email уже зарегистрирован'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(Q(email=email) | Q(username=username)).exists():
        user = User.objects.get(Q(email=email) | Q(username=username))
        send_confirmation_code(user)  # Отправляем новый confirmation code
        return Response(
            {'message': 'Новый confirmation code отправлен на почту'},
            status=status.HTTP_200_OK
        )

    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Token(APIView):
    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            confirmation_code = serializer.data['confirmation_code']
            user = get_object_or_404(User, username=username)
            if confirmation_code != user.confirmation_code:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
