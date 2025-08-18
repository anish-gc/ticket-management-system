from rest_framework import serializers


class NotificationLogReadSerializer(serializers.Serializer):
    """Read-only serializer for NotificationLog"""

    referenceId = serializers.CharField(source="reference_id", read_only=True)
    notificationType = serializers.CharField(source="notification_type", read_only=True)
    recipientId = serializers.CharField(source="recipient.referenceId", read_only=True)
    recipientName = serializers.CharField(source="recipient.full_name", read_only=True)
    senderId = serializers.CharField(source="sender.referenceId", read_only=True)
    senderName = serializers.CharField(source="sender.full_name", read_only=True)
    ticketId = serializers.CharField(source="ticket.referenceId", read_only=True)
    ticketNumber = serializers.CharField(source="ticket.ticket_number", read_only=True)

    title = serializers.CharField( read_only=True)
    message = serializers.CharField( read_only=True)

    isRead = serializers.BooleanField(source="is_read", read_only=True)
    isSent = serializers.BooleanField(source="is_sent", read_only=True)

    sentAt = serializers.DateTimeField(source="sent_at", read_only=True)
    readAt = serializers.DateTimeField(source="read_at", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
