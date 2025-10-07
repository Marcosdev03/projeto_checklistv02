from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo E-mail é obrigatório.')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, password):
        user = self.create_user(email, first_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user



class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']


class Tarefa(models.Model):
    class StatusTarefa(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em_Andamento'
        CONCLUIDA = 'CONCLUIDA', 'Concluida'

    titulo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=StatusTarefa.choices,
        default=StatusTarefa.PENDENTE,
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)


class TokenRecuperacao(models.Model):
    token = models.CharField(max_length=255, unique=True)
    data_expiracao = models.DateTimeField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)