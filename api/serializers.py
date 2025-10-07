from rest_framework import serializers
from .models import Tarefa
from .models import Usuario

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'


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