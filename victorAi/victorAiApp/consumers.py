# consumers.py
import json
import asyncio
import hashlib
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import UserChat, VictorAi, AiMemory
from .handlers import ResponseHandler

MAX_MESSAGES_PER_CONVERSATION = 20

class ChatConsumer(AsyncWebsocketConsumer):
    
    @database_sync_to_async
    def get_conversations(self):
        try:
            memories = AiMemory.objects.filter(user=None).order_by("-updated_at")[:5]
            conversations = []
            for memory in memories:
                # FIXED INDENTATION HERE
                messages = memory.messages or []
                if messages:
                    first_message = messages[0]
                    title = memory.title or first_message.get('user', '')[:50] + "..." if first_message.get('user') else "New Conversation"
                else:
                    title = memory.title or "Empty Conversation"
                
                conversations.append({
                    "id": str(memory.id),
                    "title": title,
                    "messages": messages,
                    "updated_at": memory.updated_at.isoformat() if memory.updated_at else None
                })
            return conversations
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    async def broadcast_conversations(self):
        """Broadcast conversation history to client"""
        conversations = await self.get_conversations()
        await self.send(text_data=json.dumps({
            "type": "conversation_update",
            "payload": conversations
        }))
        
    async def connect(self):
        try:
            print("WebSocket connection attempt")

            channel_hash = hashlib.md5(self.channel_name.encode()).hexdigest()[:8]
            self.room_group_name = f"chat_{channel_hash}"
            
            # Start periodic broadcasting (every 3 seconds)
            self.keep_alive = True
            asyncio.create_task(self.periodic_broadcast())

            await self.accept()
            
            # Send initial conversations immediately
            await self.broadcast_conversations()
            
        except Exception as e:
            print(f"Connection error: {e}")
            await self.close(code=4000)

    async def periodic_broadcast(self):
        """Broadcast conversations every 3 seconds"""
        while self.keep_alive:
            try:
                await self.broadcast_conversations()
                await asyncio.sleep(3)  # Broadcast every 3 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Broadcast error: {e}")
                break

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: {close_code}")
        self.keep_alive = False

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "chat_message")

            if message_type == "chat_message":
                await self.handle_chat_message(data)
            else:
                await self.send_error("Unknown message type")
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            print(f"Receive error: {e}")
            await self.send_error("Internal server error")

    async def handle_chat_message(self, data):
        user_message = data.get("message", "").strip()

        if not user_message:
            await self.send_error("Message cannot be empty")
            return

        # Generate AI response
        ai_response = await self.generate_ai_response(user_message)

        # Save to database (without user)
        conversation_id = await self.save_conversation(user_message, ai_response)

        # Send AI response
        response_data = {
            "type": "chat_response",
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": asyncio.get_event_loop().time(),
            "conversation_id": conversation_id
        }
        await self.send(text_data=json.dumps(response_data))
        
        await asyncio.sleep(0.1)
        
        # Immediately update conversations after new message
        await self.broadcast_conversations()

    async def generate_ai_response(self, user_message: str):
        """
        Delegate AI response generation to the ResponseHandler (and MathHandler internally).
        """
        try:
            response = ResponseHandler.process(user_message)
            return response or "I'm still learning, but I got your message."
        except Exception as e:
            print(f"AI Response error: {e}")
            return "Something went wrong while generating a response."
    
    @database_sync_to_async
    def save_conversation(self, user_message, ai_response):
        try:
            chat = UserChat.objects.create(
                user=None,
                message=user_message
            )

            VictorAi.objects.create(
                user_chat=chat,
                response=ai_response
            )

            latest_memory = AiMemory.objects.filter(user=None).order_by('-id').first()

            if not latest_memory or len(latest_memory.messages) >= MAX_MESSAGES_PER_CONVERSATION:
                memory = AiMemory.objects.create(
                    user=None,
                    title=user_message[:50] + "..." if len(user_message) > 50 else user_message,
                    messages=[{"user": user_message, "ai": ai_response}]
                )
            else:
                latest_memory.messages.append({"user": user_message, "ai": ai_response})
                latest_memory.save()
                memory = latest_memory
            memory.refresh_from_db()
            return str(memory.id)
        
        except Exception as e:
            print(f"Database save error: {e}")
            return None

    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": error_message
        }))