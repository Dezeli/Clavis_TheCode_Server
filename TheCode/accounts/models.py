from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, provider, provider_user_id, email=None, username=None):
        if not provider:
            raise ValueError("provider는 필수입니다.")
        if not provider_user_id:
            raise ValueError("provider_user_id는 필수입니다.")

        user = self.model(
            provider=provider,
            provider_user_id=provider_user_id,
            email=self.normalize_email(email) if email else None,
            username=username,
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError("Superuser는 email이 필요합니다.")
        if not username:
            raise ValueError("Superuser는 username이 필요합니다.")

        user = self.model(
            provider="local",
            provider_user_id=f"admin-{email}",
            email=self.normalize_email(email),
            username=username,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    


class User(AbstractBaseUser, PermissionsMixin):
    provider = models.CharField(max_length=20)       # google / apple / local(admin)
    provider_user_id = models.CharField(max_length=255, unique=True)

    email = models.EmailField(null=True, blank=True, unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.provider}:{self.provider_user_id} ({self.username})"
    


class StoredRefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    token = models.CharField(max_length=500)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    session_scope = models.CharField(max_length=20, default="local")

    revoked = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} / revoked={self.revoked}"
