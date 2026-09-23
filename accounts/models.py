from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.functions import Lower


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, name, password, **extra):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        if not name:
            raise ValueError("O nome é obrigatório.")
        user = self.model(email=self.normalize_email(email).lower(), name=name, **extra)
        user.set_password(password)  # grava o hash (PBKDF2) em `password`
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, name, password, **extra)

    def create_superuser(self, email, name, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, name, password, **extra)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Usuário autenticado por e-mail e senha."""

    name = models.CharField("nome", max_length=150)
    email = models.EmailField("e-mail", max_length=254)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        constraints = [
            # E-mail único sem diferenciar maiúsculas/minúsculas
            models.UniqueConstraint(Lower("email"), name="unique_user_email_ci"),
        ]

    def __str__(self):
        return self.email
