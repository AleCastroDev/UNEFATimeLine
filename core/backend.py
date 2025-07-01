from django.contrib.auth.backends import BaseBackend
from core.models import CedulaUser

class CedulaBackend(BaseBackend):
    def authenticate(self, request, cedula=None, password=None, **kwargs):
        try:
            user = CedulaUser.objects.get(cedula=cedula)
            if user.check_password(password):  # VERIFICAMOS CLAVE
                return user
        except CedulaUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CedulaUser.objects.get(pk=user_id)
        except CedulaUser.DoesNotExist:
            return None
