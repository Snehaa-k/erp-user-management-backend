import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from companies.models import User
from roles.models import UserRole

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def permission_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'permissionUpdate',
            'userId': event['user_id'],
            'permissions': event['permissions']
        }))

    @database_sync_to_async
    def get_user_permissions(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            user_roles = UserRole.objects.filter(user=user)
            permissions = set()
            for user_role in user_roles:
                role_permissions = user_role.role.permissions.all()
                permissions.update([perm.name for perm in role_permissions])
            return list(permissions)
        except User.DoesNotExist:
            return []