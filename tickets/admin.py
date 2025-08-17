from django.contrib import admin

from tickets.models.notification_log_model import NotificationLog
from .models import TicketStatus, TicketPriority
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "title",
        "status",
        "priority",
        "created_for",
        "assigned_to",
        "due_date",
        "sla_breached",
        "is_escalated",
    )
    list_filter = (
        "status",
        "priority",
        "sla_breached",
        "is_escalated",
    )
    search_fields = (
        "ticket_number",
        "title",
        "description",
        "created_for__username",
        "assigned_to__username",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "first_response_at",
        "resolved_at",
        "sla_due_date",
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "notification_type",
        "title",
        "recipient",
        "sender",
        "ticket",
        "is_read",
        "is_sent",
        "created_at",
        "sent_at",
        "read_at",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "is_sent",
        "created_at",
    )
    search_fields = (
        "title",
        "message",
        "recipient__username",
        "sender__username",
        "ticket__ticket_number",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "sent_at",
        "read_at",
    )
    ordering = ("-created_at",)

@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'name', 'code', 'status_type', 'weight', 'is_default')
    list_filter = ('status_type', 'is_default')
    search_fields = ('name', 'code', 'reference_id')
    ordering = ('weight', 'name')
    readonly_fields = ('reference_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reference_id', 'name', 'code', 'description')
        }),
        ('Configuration', {
            'fields': ('status_type', 'weight', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'name', 'code', 'weight', 'color', 'sla_hours', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name', 'code', 'reference_id')
    ordering = ('-weight', 'name')
    readonly_fields = ('reference_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reference_id', 'name', 'code', 'description')
        }),
        ('Priority Settings', {
            'fields': ('weight', 'color', 'sla_hours')
        }),
        ('Default Status', {
            'fields': ('is_default',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )