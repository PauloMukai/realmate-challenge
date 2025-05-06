from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Conversation, Message
from django.utils import timezone
import uuid


class WebhookAPITests(APITestCase):
    def setUp(self):
        self.webhook_url = reverse('webhook')
        self.conversation_id = str(uuid.uuid4())
        self.message_id = str(uuid.uuid4())
        self.timestamp = timezone.now().isoformat()

    def test_create_new_conversation(self):
        data = {
            "type": "NEW_CONVERSATION",
            "timestamp": self.timestamp,
            "data": {
                "id": self.conversation_id
            }
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Conversation.objects.filter(
            id=self.conversation_id).exists())

    def test_add_message_to_open_conversation(self):
        Conversation.objects.create(id=self.conversation_id)
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": self.timestamp,
            "data": {
                "id": self.message_id,
                "direction": "RECEIVED",
                "content": "Olá, tudo bem?",
                "conversation_id": self.conversation_id
            }
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(id=self.message_id).exists())

    def test_add_message_to_closed_conversation(self):
        Conversation.objects.create(id=self.conversation_id, status='CLOSED')
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": self.timestamp,
            "data": {
                "id": self.message_id,
                "direction": "RECEIVED",
                "content": "Mensagem após fechamento",
                "conversation_id": self.conversation_id
            }
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_close_conversation(self):
        Conversation.objects.create(id=self.conversation_id)
        data = {
            "type": "CLOSE_CONVERSATION",
            "timestamp": self.timestamp,
            "data": {
                "id": self.conversation_id
            }
        }
        response = self.client.post(self.webhook_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        conversation = Conversation.objects.get(id=self.conversation_id)
        self.assertEqual(conversation.status, 'CLOSED')

    def test_get_conversation_details(self):
        conversation = Conversation.objects.create(id=self.conversation_id)
        Message.objects.create(
            id=self.message_id,
            conversation=conversation,
            direction='RECEIVED',
            content='Teste de mensagem',
            timestamp=self.timestamp
        )
        url = reverse('conversation-detail', args=[self.conversation_id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.conversation_id)
        self.assertEqual(len(response.data['messages']), 1)
        self.assertEqual(response.data['messages'][0]['id'], self.message_id)
