# tickets/signals.py
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models.ticket_model import Ticket

logger = logging.getLogger("django")

# Store previous state for comparison
_ticket_previous_state = {}


@receiver(pre_save, sender=Ticket)
def store_previous_ticket_state(sender, instance, **kwargs):
    """Store the previous state of ticket before saving to detect changes."""
    if instance.pk:  # Only for existing tickets (updates)
        try:
            previous = Ticket.objects.get(pk=instance.pk)
            _ticket_previous_state[instance.pk] = {
                "assigned_to": previous.assigned_to,
                "status": previous.status,
                "priority": previous.priority,
            }
        except Ticket.DoesNotExist:
            pass
    else:
        # For new tickets, store None values
        _ticket_previous_state["new"] = {
            "assigned_to": None,
            "status": None,
            "priority": None,
        }


@receiver(post_save, sender=Ticket)
def ticket_notification_handler(sender, instance, created, **kwargs):
    """Handle notifications for ticket operations."""

    if created:
        # Ticket was created
        send_ticket_created_notification(instance)
    else:
        # Ticket was updated - check for specific changes
        previous_state = _ticket_previous_state.get(instance.pk)
        if previous_state:
            # Check for assignment/reassignment
            if previous_state["assigned_to"] != instance.assigned_to:
                send_ticket_assignment_notification(
                    instance, previous_state["assigned_to"], instance.assigned_to
                )

            # Check for other updates (status, priority, etc.)
            if (
                previous_state["status"] != instance.status
                or previous_state["priority"] != instance.priority
            ):
                send_ticket_updated_notification(instance, previous_state)

        # Clean up stored state
        if instance.pk in _ticket_previous_state:
            del _ticket_previous_state[instance.pk]


def send_ticket_created_notification(ticket):
    """Send notification when a ticket is created."""
    title = f"New Ticket Created: {ticket.title}"
    message = f"🎫 A new ticket has been created:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nPriority: {ticket.priority}\nStatus: {ticket.status}"

    # Console log
    logger.info(f"NOTIFICATION - TICKET CREATED: {title}")
    print(f"[NOTIFICATION] {title}")

    # Database log using your NotificationLog model
    log_notification_to_db(
        notification_type="ticket_created",
        ticket=ticket,
        title=title,
        message=message,
        sender=getattr(ticket, "created_by", None),
    )

    # Optional: Add email notification logic here
    # send_email_notification("ticket_created", ticket, message)


def send_ticket_updated_notification(ticket, previous_state):
    """Send notification when a ticket is updated."""
    changes = []
    notification_type = "ticket_updated"  # default

    if previous_state["status"] != ticket.status:
        changes.append(f"Status: {previous_state['status']} → {ticket.status}")
        notification_type = "status_changed"

    if previous_state["priority"] != ticket.priority:
        changes.append(f"Priority: {previous_state['priority']} → {ticket.priority}")
        if (
            notification_type == "ticket_updated"
        ):  # Only change if not already status_changed
            notification_type = "priority_changed"

    changes_text = ", ".join(changes) if changes else "General update"
    title = f"Ticket Updated: {ticket.title}"
    message = f"📝 Ticket has been updated:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nChanges: {changes_text}"

    # Console log
    logger.info(f"NOTIFICATION - TICKET UPDATED: {title} - {changes_text}")
    print(f"[NOTIFICATION] {title} - {changes_text}")

    # Database log
    log_notification_to_db(
        notification_type=notification_type,
        ticket=ticket,
        title=title,
        message=message,
        sender=getattr(ticket, "updated_by", None),
    )

    # Optional: Email notification
    # send_email_notification("ticket_updated", ticket, message)


def send_ticket_assignment_notification(ticket, previous_assignee, new_assignee):
    """Send notification when a ticket is assigned or reassigned."""
    if previous_assignee is None and new_assignee is not None:
        # New assignment
        title = f"Ticket Assigned: {ticket.title}"
        message = f"👤 You have been assigned a ticket:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nAssigned to: {new_assignee}"
        notification_type = "ticket_assigned"
    elif previous_assignee is not None and new_assignee is not None:
        # Reassignment
        title = f"Ticket Reassigned: {ticket.title}"
        message = f"🔄 Ticket has been reassigned:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nFrom: {previous_assignee}\nTo: {new_assignee}"
        notification_type = "ticket_reassigned"
    elif previous_assignee is not None and new_assignee is None:
        # Unassigned
        title = f"Ticket Unassigned: {ticket.title}"
        message = f"❌ Ticket has been unassigned:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nPreviously assigned to: {previous_assignee}"
        notification_type = "ticket_reassigned"  # Using reassigned type as unassigned isn't in your model
    else:
        return  # No change

    # Console log
    logger.info(f"NOTIFICATION - {notification_type.upper()}: {title}")
    print(f"[NOTIFICATION] {title}")

    # Database log
    log_notification_to_db(
        notification_type=notification_type,
        ticket=ticket,
        title=title,
        message=message,
        sender=getattr(ticket, "updated_by", None),
    )

    # Optional: Email notification
    # send_email_notification("ticket_assignment", ticket, message,
    #                        previous_assignee=previous_assignee, new_assignee=new_assignee)


def log_notification(notification_type, ticket, message):
    """Legacy function - kept for backward compatibility."""
    # Redirect to the new enhanced function
    log_notification_to_db(
        notification_type=notification_type.lower(),
        ticket=ticket,
        title=f"Ticket {ticket.reference_id}",
        message=message,
    )


# Optional: Email notification function
def send_email_notification(notification_type, ticket, message, **kwargs):
    """Send email notification (optional implementation)."""
    from django.core.mail import send_mail
    from django.conf import settings

    # Determine recipients based on notification type
    recipients = []

    if notification_type == "ticket_created":
        # Notify admin/support team
        recipients = [settings.ADMIN_EMAIL] if hasattr(settings, "ADMIN_EMAIL") else []
    elif notification_type == "ticket_assignment":
        # Notify the assigned user
        if ticket.assigned_to and ticket.assigned_to.email:
            recipients.append(ticket.assigned_to.email)
    elif notification_type == "ticket_updated":
        # Notify ticket creator and assigned user
        if ticket.created_for and ticket.created_for.email:
            recipients.append(ticket.created_for.email)
        if ticket.assigned_to and ticket.assigned_to.email:
            recipients.append(ticket.assigned_to.email)

    if recipients:
        try:
            send_mail(
                subject=f"Ticket Notification: {ticket.title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True,
            )
            logger.info(f"Email sent for {notification_type} to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")


# tickets/apps.py
from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tickets"

    def ready(self):
        # Import signals when the app is ready
        import tickets.signals


# Enhanced notification logging functions using your NotificationLog model
from django.utils import timezone


def log_notification_to_db(
    notification_type, ticket, title, message, sender=None, recipients=None
):
    """
    Create notification logs using your NotificationLog model.

    Args:
        notification_type: Type of notification (matches your model choices)
        ticket: Ticket instance
        title: Short summary of the notification
        message: Full content of the notification
        sender: Account who triggered the notification (optional)
        recipients: List of Account instances or single Account (optional, auto-determined if None)
    """
    try:
        from tickets.models.notification_log_model import NotificationLog
        from accounts.models.account_model import Account

        # Auto-determine recipients if not provided
        if recipients is None:
            recipients = determine_notification_recipients(
                notification_type, ticket, sender
            )
        elif not isinstance(recipients, list):
            recipients = [recipients]

        # Create notification for each recipient
        notifications_created = []
        for recipient in recipients:
            if recipient:  # Ensure recipient is not None
                notification = NotificationLog.objects.create(
                    notification_type=notification_type,
                    recipient=recipient,
                    sender=sender,
                    ticket=ticket,
                    title=title,
                    message=message,
                    is_sent=True,  # Mark as sent since we're creating it
                    sent_at=timezone.now(),
                )
                notifications_created.append(notification)

        logger.info(
            f"Created {len(notifications_created)} notification(s) for {notification_type} - ticket {ticket.reference_id}"
        )
        return notifications_created

    except Exception as e:
        logger.error(f"Failed to log notification to database: {e}")
        # Fallback to regular logging
        logger.info(f"FALLBACK LOG - {notification_type}: {title} - {message}")
        return []


def determine_notification_recipients(notification_type, ticket, sender=None):
    """
    Automatically determine who should receive notifications based on type and ticket details.
    """
    recipients = []

    try:
        # Ticket created - notify admins and assigned user
        if notification_type == "ticket_created":
            if ticket.assigned_to:
                recipients.append(ticket.assigned_to)
            # You can add admin notification logic here
            # recipients.extend(get_admin_users())

        # Ticket assigned/reassigned - notify the assigned user
        elif notification_type in ["ticket_assigned", "ticket_reassigned"]:
            if ticket.assigned_to:
                recipients.append(ticket.assigned_to)

        # Ticket updated - notify creator, assigned user (excluding sender to avoid self-notification)
        elif notification_type in [
            "ticket_updated",
            "status_changed",
            "priority_changed",
        ]:
            if ticket.created_for and ticket.created_for != sender:
                recipients.append(ticket.created_for)
            if ticket.assigned_to and ticket.assigned_to != sender:
                recipients.append(ticket.assigned_to)

        # Due date approaching - notify assigned user and creator
        elif notification_type == "due_date_approaching":
            if ticket.assigned_to:
                recipients.append(ticket.assigned_to)
            if ticket.created_for and ticket.created_for != ticket.assigned_to:
                recipients.append(ticket.created_for)

    except Exception as e:
        logger.error(f"Error determining notification recipients: {e}")

    # Remove duplicates while preserving order
    seen = set()
    unique_recipients = []
    for recipient in recipients:
        if recipient and recipient.id not in seen:
            seen.add(recipient.id)
            unique_recipients.append(recipient)

    return unique_recipients


def get_admin_users():
    """Helper function to get admin users for notifications."""
    try:
        from accounts.models import Account

        # Adjust this query based on your admin user identification logic
        return Account.objects.filter(role='admin', is_active=True)
    except Exception as e:
        logger.error(f"Error fetching admin users: {e}")
        return []


# Utility function to mark notifications as read
def mark_notification_as_read(notification_id, user):
    """Mark a notification as read by the user."""
    try:
        from tickets.models.notification_log_model import NotificationLog

        notification = NotificationLog.objects.get(
            id=notification_id, recipient=user, is_read=False
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        logger.info(f"Notification {notification_id} marked as read by {user}")
        return notification

    except NotificationLog.DoesNotExist:
        logger.warning(
            f"Notification {notification_id} not found or already read by {user}"
        )
        return None
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return None
