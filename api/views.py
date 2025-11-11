# api/views.py

from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny # Importe AllowAny
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao # Verifique se TokenRecuperacao está em models.py
from .serializers import (
    UsuarioSerializer,
    TarefaSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
import secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend # Importe o backend de filtro

# ==================================
#    TAREFA VIEWSET (Estava faltando!)
# ==================================
class TarefaViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar Tarefas."""
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated, IsOwner] # Garante que só o dono veja/edite
    filter_backends = [DjangoFilterBackend] # Habilita filtros
    filterset_fields = ['status'] # Permite filtrar por status (ex: /api/tarefas/?status=PENDENTE)

    def get_queryset(self):
        """
        Esta view deve retornar uma lista de todas as tarefas
        para o usuário autenticado atualmente.
        """
        # Durante a geração do schema (drf-spectacular) a view é instanciada com
        # uma request falsa/anonima. Garantimos que isso não levante exceções
        # acessando atributos de `request.user` e retornando queryset vazio.
        if getattr(self, 'swagger_fake_view', False):
            return Tarefa.objects.none()

        user = getattr(self.request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            # retornar queryset vazio para usuários não autenticados
            return Tarefa.objects.none()

        # O filter já garante que o usuário só veja suas próprias tarefas
        return Tarefa.objects.filter(usuario=user).order_by('-data_criacao') # Ordena pelas mais recentes

    def perform_create(self, serializer):
        """Associa o usuário logado automaticamente à nova tarefa."""
        serializer.save(usuario=self.request.user)

    # --- Decoradores @extend_schema para Documentação ---
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
#    USUARIO VIEWSET (Apenas uma vez e corrigido)
# ==================================
class UsuarioViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar o próprio Usuário e criar novas contas."""
    serializer_class = UsuarioSerializer
    # queryset = Usuario.objects.all() # Removido para segurança

    def get_queryset(self):
        """Usuários logados só podem ver/editar a si mesmos."""
        user = self.request.user
        if user.is_authenticated:
            return Usuario.objects.filter(pk=user.pk) # pk é a chave primária
        return Usuario.objects.none()

    def get_permissions(self):
        """Permite 'create' (registro) para qualquer um, outras ações exigem login."""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            # Garante que só o próprio usuário possa ver/editar/deletar
            # Você pode criar uma permissão customizada "IsSelf" se quiser ser mais explícito
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # --- Decoradores @extend_schema para Documentação ---
    @extend_schema(summary="Ver meus dados de usuário")
    def list(self, request, *args, **kwargs):
        # A lógica do get_queryset já filtra para o usuário atual
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar um novo usuário (Registro)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Ver meus dados de usuário (pelo ID - redundante com list)")
    def retrieve(self, request, *args, **kwargs):
        # A lógica do get_queryset já filtra, mas a permissão IsAuthenticated garante
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
    permission_classes = [AllowAny] # Qualquer um pode solicitar

    @extend_schema(summary="Solicitar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Não revele que o usuário não existe por segurança
            return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)

        # Remove tokens antigos para este usuário, se houver
        TokenRecuperacao.objects.filter(usuario=user).delete()

        token_str = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1) # Token válido por 1 hora

        TokenRecuperacao.objects.create(
            usuario=user,
            token=token_str,
            data_expiracao=expires_at
        )

        # Tenta enviar um email real; se falhar, cai no fallback que imprime o token.
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            subject = 'Redefinição de senha - Projeto Checklist'
            message = (
                f"Use o seguinte token para resetar sua senha: {token_str}\n\n"
                f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}"
            )
            send_mail(subject, message, from_email, [email])
        except Exception as e:
            # Fallback: log simples (em produção use logging)
            print(f"Falha ao enviar email: {e}")
            print(f"--- SIMULAÇÃO DE ENVIO DE EMAIL ---")
            print(f"Para: {email}")
            print(f"Use o seguinte token para resetar sua senha: {token_str}")
            print(f"Link (exemplo): http://seu-frontend.com/reset-password?token={token_str}")
            print(f"---------------------------------")

        return Response({"detail": "Se um usuário com este email existir, um link/código foi enviado."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """View para confirmar a redefinição de senha usando o token."""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny] # Qualquer um pode tentar confirmar

    @extend_schema(summary="Confirmar redefinição de senha")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            token = TokenRecuperacao.objects.get(token=token_str)
        except TokenRecuperacao.DoesNotExist:
            return Response({"error": "Token inválido ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        if token.data_expiracao < timezone.now():
            token.delete()
            return Response({"error": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user = token.usuario
        user.set_password(new_password) # set_password faz o hash
        user.save()
        token.delete() # Token só pode ser usado uma vez

        return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)