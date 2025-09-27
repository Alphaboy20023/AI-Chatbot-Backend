import uuid
from rest_framework import serializers
from .models import CustomUser, VictorAi, AiMemory, UserChat
from .handlers import MathHandler, PROMPTS
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
MAX_MESSAGES_PER_CONVERSATION = 20


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']


class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChat
        fields = ["id", "user", "message", "created_at"]
        read_only_fields = ['user', 'created_at']
        
        
class CustomUserTokenObtainSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.USERNAME_FIELD 

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email is None or password is None:
            raise serializers.ValidationError("Email and password are required")
        return super().validate(attrs)


def generate_ai_reply(user_message):
    """Simple AI reply logic based on prompts."""
    if not user_message:
        return PROMPTS.get("default")
    message = user_message.lower()
    for keyword, reply in PROMPTS.items():
        if keyword in message:
            return reply
    return PROMPTS.get("default")


class ConversationSerializer(serializers.Serializer):
    """
    Handles a single user->AI message interaction.
    Updates AiMemory with a new title after a threshold of messages.
    """
    message = serializers.CharField(write_only=True)
    user_message = serializers.CharField(read_only=True)
    ai_response = serializers.CharField(read_only=True)
    conversation_history = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )
    title = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user_message = validated_data['message']
        user = self.context.get('user')  # WebSocket should pass user in context

        # Save user message
        chat = UserChat.objects.create(user=user, message=user_message)

        # Generate AI reply
        math_result = MathHandler.process(user_message)
        if math_result is not None and any(op in user_message for op in "+-*/"):
            ai_reply = f"The result of {(user_message)} is {math_result}, {generate_ai_reply(user_message)}"
        else:
            ai_reply = generate_ai_reply(user_message)

        # Save AI response
        VictorAi.objects.create(user_chat=chat, response=ai_reply)

        # Update conversation memory
        latest_memory = AiMemory.objects.filter(user=user).order_by('-id').first()

        if not latest_memory or len(latest_memory.messages) >= MAX_MESSAGES_PER_CONVERSATION:
            # Start a new conversation memory with a new title
            memory = AiMemory.objects.create(
                user=user,
                title=user_message,
                messages=[{"user": user_message, "ai": ai_reply}]
            )
        else:
            # Append to existing memory
            latest_memory.messages.append({"user": user_message, "ai": ai_reply})
            latest_memory.save()
            memory = latest_memory

        return {
            "user_message": user_message,
            "ai_response": ai_reply,
            "conversation_history": [
                f"{m['user']} | {m['ai']}" for m in memory.messages
            ],
            "title": memory.title
        }
