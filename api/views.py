from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Usuario, Tarefa, TokenRecuperacao # Adicione TokenRecuperacao
from .serializers import (
    UsuarioSerializer,
    TarefaSerializer,
    PasswordResetRequestSerializer,# Adicione este serializer
    PasswordResetConfirmSerializer
)
import secrets
from django.utils import timezone
from datetime import timedelta


class TarefaViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar Tarefas."""
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ['status', 'usuario']

    def get_queryset(self):
        """
        Esta view deve retornar uma lista de todas as tarefas
        para o usuário autenticado atualmente.
        """
        user = self.request.user
        return Tarefa.objects.filter(usuario=user)

    @extend_schema(
        summary="Listar todas as tarefas",
        description="Retorna uma lista com todas as tarefas cadastradas no sistema."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Criar uma nova tarefa",
        description="Cria um novo registro de tarefa no banco de dados."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Pesquisar uma tarefa por ID",
        description="Pesquisa uma tarefa pelo ID e retorna seus dados.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID da tarefa")]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar uma tarefa (substituição completa)",
        description="Atualiza todos os campos de uma tarefa com base no ID informado.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID da tarefa")]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar parcialmente uma tarefa",
        description="Atualiza apenas os campos enviados no corpo da requisição.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID da tarefa")]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Deletar uma tarefa",
        description="Remove uma tarefa do sistema com base no ID informado.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID da tarefa")]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)




class UsuarioViewSet(viewsets.ModelViewSet):
    """Endpoint para gerenciar Usuários."""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @extend_schema(
        summary="Listar todos os usuários",
        description="Retorna uma lista com todos os usuários cadastrados no sistema."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Criar um novo usuário",
        description="Cria um novo registro de usuário no banco de dados."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Pesquisar um usuário por ID",
        description="Pesquisa um usuário pelo ID e retorna seus dados.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID do usuário")]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar um usuário (substituição completa)",
        description="Atualiza todos os campos de um usuário com base no ID informado.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID do usuário")]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar parcialmente um usuário",
        description="Atualiza apenas os campos enviados no corpo da requisição.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID do usuário")]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Deletar um usuário",
        description="Remove um usuário do sistema com base no ID informado.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH, description="ID do usuário")]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PasswordResetRequestView(generics.GenericAPIView):
    """
    View para solicitar a redefinição de senha.
    """
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Não revele que o usuário não existe por segurança
            return Response(
                {"detail": "Se um usuário com este email existir, um link de redefinição foi enviado."},
                status=status.HTTP_200_OK
            )

        # Gera um token seguro
        token = secrets.token_urlsafe(32)

        # Define a data de expiração (ex: 1 hora a partir de agora)
        expires_at = timezone.now() + timedelta(hours=1)

        # Salva o token no banco de dados
        TokenRecuperacao.objects.create(
            usuario=user,
            token=token,
            data_expiracao=expires_at
        )

        # Em um projeto real, aqui você enviaria um e-mail para o usuário com o token.
        # Por enquanto, vamos apenas retorná-lo na resposta para facilitar os testes.
        print(f"Link para resetar a senha: http://seusite.com/reset-password?token={token}")

        return Response(
            {"detail": "Se um usuário com este email existir, um link de redefinição foi enviado."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    View para confirmar a redefinição de senha.
    """
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # 1. Valida os dados (token e senhas)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        # 2. Busca o token no banco de dados
        try:
            token = TokenRecuperacao.objects.get(token=token_str)
        except TokenRecuperacao.DoesNotExist:
            return Response({"erro": "Token inválido ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Verifica se o token expirou
        if token.data_expiracao < timezone.now():
            token.delete()  # Apaga o token expirado
            return Response({"erro": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Altera a senha do usuário associado ao token
        user = token.usuario
        user.set_password(new_password)  # set_password criptografa a nova senha
        user.save()

        # 5. Apaga o token para que não possa ser usado novamente
        token.delete()

        return Response({"detalhe": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)