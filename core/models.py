from django.db import models

# Create your models here.


class Conversation(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    id = models.UUIDField(primary_key=True)
    status = models.CharField(
        max_length=6, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['id'], name='unique_conversation_id')
        ]

    def __str__(self):
        return f"Conversation {self.id} - {self.status}"


class Message(models.Model):
    DIRECTION_CHOICES = [
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    ]
    id = models.UUIDField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation, related_name='messages', on_delete=models.CASCADE)
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='unique_message_id')
        ]

    def __str__(self):
        return f"Message {self.id} - {self.direction}"
