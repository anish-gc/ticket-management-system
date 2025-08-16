from django.contrib import admin
from .models import TicketStatus, TicketPriority

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