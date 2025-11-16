from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # O modelo `Tarefa` e `TokenRecuperacao` usam o campo `usuario`.
        # Comparar com `obj.user` resulta em AttributeError ou comparação incorreta.
        # Suportamos também `user` por compatibilidade com outros modelos, se existirem.
        owner = getattr(obj, 'usuario', None)
        if owner is None:
            owner = getattr(obj, 'user', None)
        return owner == request.user