from itsdangerous import URLSafeTimedSerializer as utsr
from django.conf import settings as django_settings
from itsdangerous import BadSignature,SignatureExpired


class Token:
    def __init__(self, security_key):
        self.security_key = security_key
        self.salt = security_key

    def generate_validate_token(self, user_id):
        serializer = utsr(self.security_key)
        return serializer.dumps(user_id, self.salt)

    def confirm_validate_token(self, token, expiration=3600):
        serializer = utsr(self.security_key)
        try:
            user_id = serializer.loads(token, salt=self.salt, max_age=expiration)
        except BadSignature:
            return -1, '无效的激活码'
        except SignatureExpired:
            return -1, '激活码已过期'
        return user_id, None

    def get_validate_token(self, token):
        serializer = utsr(self.security_key)
        return serializer.loads(token, salt=self.salt)


token_manager = Token(django_settings.SECRET_KEY)
