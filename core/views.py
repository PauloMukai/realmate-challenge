from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer


class WebhookView(APIView):
    def post(self, request):
        event_type = request.data.get('type')
        data = request.data.get('data')
        timestamp = request.data.get('timestamp')

        if event_type == 'NEW_CONVERSATION':
            conversation_id = data.get('id')
            if not Conversation.objects.filter(id=conversation_id).exists():
                Conversation.objects.create(id=conversation_id)
            return Response({'message': 'Conversation created'}, status=status.HTTP_201_CREATED)

        elif event_type == 'NEW_MESSAGE':
            message_id = data.get('id')
            direction = data.get('direction')
            content = data.get('content')
            conversation_id = data.get('conversation_id')

            conversation = Conversation.objects.filter(
                id=conversation_id).first()
            if not conversation:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_400_BAD_REQUEST)
            if conversation.status == 'CLOSED':
                return Response({'error': 'Cannot add message to closed conversation'}, status=status.HTTP_400_BAD_REQUEST)
            if not Message.objects.filter(id=message_id).exists():
                Message.objects.create(
                    id=message_id,
                    conversation=conversation,
                    direction=direction,
                    content=content,
                    timestamp=parse_datetime(timestamp)
                )
            return Response({'message': 'Message added'}, status=status.HTTP_201_CREATED)

        elif event_type == 'CLOSE_CONVERSATION':
            conversation_id = data.get('id')
            conversation = Conversation.objects.filter(
                id=conversation_id).first()
            if conversation:
                conversation.status = 'CLOSED'
                conversation.save()
                return Response({'message': 'Conversation closed'}, status=status.HTTP_200_OK)
            return Response({'error': 'Conversation not found'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Invalid event type'}, status=status.HTTP_400_BAD_REQUEST)


class ConversationDetailView(APIView):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)
