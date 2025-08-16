

class NotificationLog(models.Model):
    """Log all notifications sent"""
    NOTIFICATION_TYPE_CHOICES = [
        ('ticket_created', 'Ticket Created'),
        ('ticket_updated', 'Ticket Updated'),
        ('ticket_assigned', 'Ticket Assigned'),
        ('ticket_reassigned', 'Ticket Reassigned'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('comment_added', 'Comment Added'),
        ('due_date_approaching', 'Due Date Approaching'),
    ]
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Delivery status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(default=dict, blank=True)  # For additional notification data
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.username}"