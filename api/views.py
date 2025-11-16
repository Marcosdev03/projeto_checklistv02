"""API views for the Projeto Checklist project.

This file contains the viewsets and API views used by DRF. It was
rewritten to remove accidental markdown fences and duplicated blocks.
"""

from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao
from .serializers import (
    UsuarioSerializer,
    TarefaSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
import secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend


class TarefaViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar Tarefas."""
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Tarefa.objects.none()
        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return Tarefa.objects.none()
        return Tarefa.objects.filter(usuario=user).order_by("-data_criacao")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(summary="Listar minhas tarefas")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar uma nova tarefa")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UsuarioViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar o próprio Usuário e criar novas contas."""
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Usuario.objects.filter(pk=user.pk)
        return Usuario.objects.none()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Solicitar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)

        TokenRecuperacao.objects.filter(usuario=user).delete()

        token_str = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        TokenRecuperacao.objects.create(
            usuario=user,
            token=token_str,
            data_expiracao=expires_at,
        )

        try:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            subject = "Redefinição de senha - Projeto Checklist"
            message = (
                f"Use o seguinte token para resetar sua senha: {token_str}\n\n"
                f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}"
            )
            send_mail(subject, message, from_email, [email])
        except Exception:
            # fallback: do not crash schema generation if email backend missing
            pass

        return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Confirmar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            token = TokenRecuperacao.objects.get(token=token_str)
        except TokenRecuperacao.DoesNotExist:
            return Response({"error": "Token inválido ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        if token.data_expiracao < timezone.now():
            token.delete()
            return Response({"error": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user = token.usuario
        user.set_password(new_password)
        user.save()
        token.delete()
        return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
"""api/views.py

Clean, corrected API views for the project.
"""

from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao
from .serializers import (
    UsuarioSerializer,
    TarefaSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
import secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend


# ==================================
#    TAREFA VIEWSET
# ==================================
class TarefaViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar Tarefas."""
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Tarefa.objects.none()

        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return Tarefa.objects.none()

        return Tarefa.objects.filter(usuario=user).order_by("-data_criacao")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(summary="Listar minhas tarefas")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar uma nova tarefa")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Ver detalhes de uma tarefa")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar uma tarefa (completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar parcialmente uma tarefa")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Deletar uma tarefa")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ==================================
#    USUARIO VIEWSET
# ==================================
class UsuarioViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar o próprio Usuário e criar novas contas."""
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Usuario.objects.filter(pk=user.pk)
        return Usuario.objects.none()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(summary="Ver meus dados de usuário")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar um novo usuário (Registro)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Ver meus dados de usuário (pelo ID - redundante com list)")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar meus dados (completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar meus dados (parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Deletar minha conta de usuário")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ==================================
#    PASSWORD RESET VIEWS
# ==================================
class PasswordResetRequestView(generics.GenericAPIView):
    """View para solicitar a redefinição de senha."""
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Solicitar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)

        TokenRecuperacao.objects.filter(usuario=user).delete()

        token_str = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        TokenRecuperacao.objects.create(
            usuario=user,
            token=token_str,
            data_expiracao=expires_at,
        )

        try:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            subject = "Redefinição de senha - Projeto Checklist"
            message = (
                f"Use o seguinte token para resetar sua senha: {token_str}\n\n"
                f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}"
            )
            send_mail(subject, message, from_email, [email])
        except Exception as e:
            print(f"Falha ao enviar email: {e}")
            print(f"--- SIMULAÇÃO DE ENVIO DE EMAIL ---")
            print(f"Para: {email}")
            print(f"Use o seguinte token para resetar sua senha: {token_str}")
            print(f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}")
            print("---------------------------------")

        return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """View para confirmar a redefinição de senha usando o token."""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Confirmar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            token = TokenRecuperacao.objects.get(token=token_str)
        except TokenRecuperacao.DoesNotExist:
            return Response({"error": "Token inválido ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        if token.data_expiracao < timezone.now():
            token.delete()
            return Response({"error": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user = token.usuario
        user.set_password(new_password)
        user.save()
        token.delete()

        return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
# api/views.py

from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny # Importe AllowAny
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao # Verifique se TokenRecuperacao está em models.py
from .serializers import (

    # api/views.py

    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
# api/views.py

from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao
from .serializers import (
    UsuarioSerializer,
    TarefaSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
import secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend


# ==================================
#    TAREFA VIEWSET
# api/views.py

from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao
from .serializers import (
    UsuarioSerializer,
    TarefaSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
import secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend


# ==================================
#    TAREFA VIEWSET
# ==================================
class TarefaViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar Tarefas."""
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Tarefa.objects.none()

        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return Tarefa.objects.none()

        return Tarefa.objects.filter(usuario=user).order_by("-data_criacao")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(summary="Listar minhas tarefas")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar uma nova tarefa")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Ver detalhes de uma tarefa")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar uma tarefa (completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar parcialmente uma tarefa")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Deletar uma tarefa")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ==================================
#    USUARIO VIEWSET
# ==================================
class UsuarioViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar o próprio Usuário e criar novas contas."""
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Usuario.objects.filter(pk=user.pk)
        return Usuario.objects.none()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(summary="Ver meus dados de usuário")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar um novo usuário (Registro)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Ver meus dados de usuário (pelo ID - redundante com list)")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar meus dados (completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar meus dados (parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Deletar minha conta de usuário")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ==================================
#    PASSWORD RESET VIEWS
# ==================================
class PasswordResetRequestView(generics.GenericAPIView):
    """View para solicitar a redefinição de senha."""
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Solicitar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)

        TokenRecuperacao.objects.filter(usuario=user).delete()

        token_str = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        TokenRecuperacao.objects.create(
            usuario=user,
            token=token_str,
            data_expiracao=expires_at,
        )

        try:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            subject = "Redefinição de senha - Projeto Checklist"
            message = (
                f"Use o seguinte token para resetar sua senha: {token_str}\n\n"
                f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}"
            )
            send_mail(subject, message, from_email, [email])
        except Exception as e:
            print(f"Falha ao enviar email: {e}")
            print(f"--- SIMULAÇÃO DE ENVIO DE EMAIL ---")
            print(f"Para: {email}")
            print(f"Use o seguinte token para resetar sua senha: {token_str}")
            print(f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}")
            print("---------------------------------")

        return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """View para confirmar a redefinição de senha usando o token."""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Confirmar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            token = TokenRecuperacao.objects.get(token=token_str)
        except TokenRecuperacao.DoesNotExist:
            return Response({"error": "Token inválido ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        if token.data_expiracao < timezone.now():
            token.delete()
            return Response({"error": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user = token.usuario
        user.set_password(new_password)
        user.save()
        token.delete()

        return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)