from rest_framework import serializers
from .models import Tarefa
from .models import Usuario

from rest_framework import serializers
from .models import Tarefa, Usuario


# api/serializers.py
class TarefaSerializer(serializers.ModelSerializer):
    # Torna o campo 'usuario' somente leitura.
    # Ele será preenchido automaticamente pela view, não enviado pelo cliente.
    # Expor o id do usuário como campo `usuario` e o email como `usuario_email`.
    usuario = serializers.ReadOnlyField(source='usuario.id')
    usuario_email = serializers.ReadOnlyField(source='usuario.email')

    class Meta:
        model = Tarefa
        # Remova 'usuario' de 'fields' se estiver explícito, ou use 'read_only_fields'
        fields = ['id', 'titulo', 'descricao', 'status', 'data_criacao', 'usuario', 'usuario_email']
        read_only_fields = ['usuario', 'usuario_email']


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usamos o nosso UserManager para criar o usuário
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            password=validated_data['password']
        )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer para solicitar a redefinição de senha. Apenas valida o email.
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para confirmar a redefinição de senha com o token.
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return data