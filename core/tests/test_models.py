import pytest
from core.models import Conversation, Message
from django.utils import timezone


@pytest.mark.django_db
def test_create_conversation():
    conversation = Conversation.objects.create(client_name="João")
    assert conversation.pk is not None
    assert conversation.client_name == "João"


@pytest.mark.django_db
def test_create_message():
    conversation = Conversation.objects.create(client_name="Maria")
    message = Message.objects.create(
        conversation=conversation,
        sender="client",
        content="Olá, tudo bem?",
        timestamp=timezone.now()
    )

    assert message.pk is not None
    assert message.conversation == conversation
    assert message.sender == "client"
    assert message.content == "Olá, tudo bem?"


@pytest.mark.django_db
def test_message_relationship():
    conversation = Conversation.objects.create(client_name="Carlos")
    Message.objects.create(conversation=conversation,
                           sender="client", content="Oi")
    Message.objects.create(conversation=conversation,
                           sender="agent", content="Olá!")

    messages = conversation.message_set.all()
    assert messages.count() == 2
