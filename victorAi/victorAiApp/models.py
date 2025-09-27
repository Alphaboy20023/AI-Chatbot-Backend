from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid


# Create your models here.
class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    is_bot = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.username}'
    
    
class TimeStampField(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class VictorAi(TimeStampField):
    user_chat = models.ForeignKey('UserChat', on_delete=models.CASCADE, related_name='ai_responses')
    response = models.TextField()
    model_name = models.CharField(max_length=100, default='V1')
    
    def __str__(self):
        return f'{self.model_name}'
    
class UserChat(TimeStampField):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats', null=True)
    message = models.TextField()
    
    def __str__(self):
        return f"{self.user}: {self.message[:30]}"
    
class AiMemory(TimeStampField):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="ai_conversations", null=True)
    messages = models.JSONField(default=list)
    title = models.TextField(blank=True)
    
    def __str__(self):
        return f"Conversation history for {self.user}"
    
    def log_user_message(self, user_chat: UserChat):
        self.messages.append({
            "role": "user",
            "content": user_chat.message,
            "timestamp": user_chat.created_at.isoformat(),
        })
        self.save()
    
    def log_ai_reply(self, ai_message: VictorAi):
        self.messages.append({
            "role": "Assistant",
            "content": ai_message.response,
            "timestamp": ai_message.created_at.isoformat(),
        })
        self.save()
        
    def get_conversation(self):
        return self.messages
    
    