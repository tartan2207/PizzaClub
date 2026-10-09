from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.account.models import CustomerUser
from apps.core.validators import normalize_phone


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = [  'id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'birth_date',
                    'phone',
                    'adress',
                    'avatar',
                    'is_staff',
                    'is_active',
                    'date_joined',
                    'is_admin',
                    'is_superuser']
        read_only_fields = ['is_staff',
                            'is_active',
                            'is_admin',
                            'is_superuser']

    def validate_phone(self, value: str) -> str:
        return normalize_phone(value) if value else ""

User = get_user_model()
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={"min_length": "Пароль повинен містити щонайменше 8 символів."}
    )
    confirm_password = serializers.CharField(write_only=True)
    username = serializers.CharField(
        max_length=150,
        min_length=3,
        error_messages={
            "min_length": "Ім'я користувача повинно містити щонайменше 3 символи."
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate_username(self, value: str) -> str:
        """Проверка уникальности username без учета регистра."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Користувач з таким іменем вже існує.")
        return value

    def validate_email(self, value: str) -> str:
        """Проверка уникальности email без учета регистра."""
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Користувач з таким email вже існує.")
        return email

    def validate(self, attrs):
        """Проверка совпадения паролей."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Паролі не збігаються."})
        return attrs

    def create(self, validated_data):
        # Удаляем лишнее поле, которое не нужно сохранять в модель
        validated_data.pop('confirm_password')

        # Извлекаем данные
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        # Создаем пользователя через менеджер моделей (пароль автоматически хешируется)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token