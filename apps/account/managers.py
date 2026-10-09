from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self,username=None, email=None,  password=None,**extra_fields):
        """
        Create and save a user with the given email and password.
        """
        # if not email:
        #     raise ValueError("The Email must be set")

        # if not username:
        #     raise ValueError("Имя пользователя (username) обязательно")
        if not username and not email:
            raise ValueError(
                "Пользователь должен иметь username или email"
            )
        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,username=None, email=None,  password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        user = self.create_user(username, email, password, **extra_fields )
        return user