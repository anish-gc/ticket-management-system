# tickets/signals.py
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
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
                "title": previous.title,
                "description": previous.description,
                "due_date": previous.due_date,
            }
        except Ticket.DoesNotExist:
            pass
    else:
        # For new tickets, store None values
        _ticket_previous_state["new"] = {
            "assigned_to": None,
            "status": None,
            "priority": None,
            "title": None,
            "description": None,
            "due_date": None,
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
            changes = detect_ticket_changes(instance, previous_state)
            if changes:
                send_ticket_updated_notification(instance, previous_state, changes)

        # Clean up stored state
        if instance.pk in _ticket_previous_state:
            del _ticket_previous_state[instance.pk]


def detect_ticket_changes(ticket, previous_state):
    """Detect and format changes made to the ticket."""
    changes = []

    if previous_state["status"] != ticket.status:
        changes.append(
            f"Status changed from '{previous_state['status']}' to '{ticket.status}'"
        )

    if previous_state["priority"] != ticket.priority:
        changes.append(
            f"Priority changed from '{previous_state['priority']}' to '{ticket.priority}'"
        )

    if previous_state["title"] != ticket.title:
        changes.append(f"Title updated")

    if previous_state["due_date"] != ticket.due_date:
        if previous_state["due_date"] is None:
            changes.append(f"Due date set to {ticket.due_date.strftime('%B %d, %Y')}")
        elif ticket.due_date is None:
            changes.append(f"Due date removed")
        else:
            changes.append(
                f"Due date changed to {ticket.due_date.strftime('%B %d, %Y')}"
            )

    return changes


def send_ticket_created_notification(ticket):
    """Send notification when a ticket is created."""
    title = f"New Ticket Created: {ticket.title}"
    message = f"🎫 A new ticket has been created:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nPriority: {ticket.priority}\nStatus: {ticket.status}"
    # Console log
    logger.info(f"NOTIFICATION - TICKET CREATED: {title}")
    print(f"[NOTIFICATION] {title}")

    # Database log
    recipients = log_notification_to_db(
        notification_type="ticket_created",
        ticket=ticket,
        title=title,
        message=message,
        sender=getattr(ticket, "created_by", None),
    )

    # Send email notifications
    send_email_notifications_for_ticket(
        notification_type="ticket_created", ticket=ticket, recipients=recipients
    )


def send_ticket_updated_notification(ticket, previous_state, changes):
    """Send notification when a ticket is updated."""
    notification_type = "ticket_updated"

    # Determine specific notification type based on changes
    if any("Status changed" in change for change in changes):
        notification_type = "status_changed"
    elif any("Priority changed" in change for change in changes):
        notification_type = "priority_changed"

    changes_text = ", ".join(changes) if changes else "General update"
    title = f"Ticket Updated: {ticket.title}"
    message = f"📝 Ticket has been updated:\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nChanges: {changes_text}"

    # Console log
    logger.info(f"NOTIFICATION - TICKET UPDATED: {title} - {changes_text}")
    print(f"[NOTIFICATION] {title} - {changes_text}")

    # Database log
    recipients = log_notification_to_db(
        notification_type=notification_type,
        ticket=ticket,
        title=title,
        message=message,
        sender=getattr(ticket, "updated_by", None),
    )

    # Send email notifications
    send_email_notifications_for_ticket(
        notification_type=notification_type,
        ticket=ticket,
        recipients=recipients,
        changes=changes,
    )


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
        notification_type = "ticket_reassigned"
    else:
        return  # No change

    # Console log
    logger.info(f"NOTIFICATION - {notification_type.upper()}: {title}")
    print(f"[NOTIFICATION] {title}")

    # Database log
    recipients = log_notification_to_db(
        notification_type=notification_type,
        ticket=ticket,
        title=title,
        message=message,
        sender=getattr(ticket, "updated_by", None),
    )

    # Send email notifications
    send_email_notifications_for_ticket(
        notification_type=notification_type,
        ticket=ticket,
        recipients=recipients,
        previous_assignee=previous_assignee,
        new_assignee=new_assignee,
    )


def send_email_notifications_for_ticket(
    notification_type, ticket, recipients, **extra_data
):
    """
    Send email notifications to all recipients for a ticket event.

    Args:
        notification_type: Type of notification
        ticket: Ticket instance
        recipients: List of user objects to notify
        **extra_data: Additional data for the email template
    """
    if not recipients:
        return

    from .utils.email_utils import send_ticket_notification_email

    successful_sends = 0
    failed_sends = 0

    for recipient in recipients:
        if recipient and recipient.email:
            try:
                success = send_ticket_notification_email(
                    user=recipient,
                    notification_type=notification_type,
                    ticket=ticket,
                    **extra_data,
                )
                if success:
                    successful_sends += 1
                else:
                    failed_sends += 1

            except Exception as e:
                logger.error(f"Failed to send email to {recipient.email}: {e}")
                failed_sends += 1

    logger.info(
        f"Email notifications for {notification_type}: {successful_sends} sent, {failed_sends} failed"
    )


# Enhanced notification logging functions using your NotificationLog model
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

    Returns:
        List of recipient users for email notifications
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

        return recipients  # Return recipients for email sending

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
            # Add admin notification logic here if needed
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
        return Account.objects.filter(role="admin", is_active=True)
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




def get_unread_notifications_count(user):
    """Get count of unread notifications for a user."""
    try:
        from tickets.models.notification_log_model import NotificationLog

        return NotificationLog.objects.filter(recipient=user, is_read=False).count()
    except Exception as e:
        logger.error(f"Error getting unread notifications count: {e}")
        return 0


def mark_all_notifications_as_read(user):
    """Mark all notifications as read for a user."""
    try:
        from tickets.models.notification_log_model import NotificationLog

        updated = NotificationLog.objects.filter(recipient=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

        logger.info(f"Marked {updated} notifications as read for {user}")
        return updated

    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return 0


def send_due_date_reminders():
    """
    Function to send reminders for tickets approaching due date.
    This can be called by a cron job or Celery task.
    """
    try:
        from datetime import timedelta

        # Get tickets due within next 24 hours
        tomorrow = timezone.now() + timedelta(days=1)
        tickets_due_soon = Ticket.objects.filter(
            due_date__lte=tomorrow,
            due_date__gte=timezone.now(),
            status__in=["open", "in_progress"],  # Only active tickets
        )

        for ticket in tickets_due_soon:
            title = f"Due Date Reminder: {ticket.title}"
            message = f"⏰ Reminder: This ticket is due soon.\n\nTitle: {ticket.title}\nID: {ticket.reference_id}\nDue: {ticket.due_date.strftime('%B %d, %Y')}"

            # Log to database
            recipients = log_notification_to_db(
                notification_type="due_date_approaching",
                ticket=ticket,
                title=title,
                message=message,
            )

            # Send email notifications
            send_email_notifications_for_ticket(
                notification_type="due_date_approaching",
                ticket=ticket,
                recipients=recipients,
            )

        logger.info(f"Processed due date reminders for {len(tickets_due_soon)} tickets")

    except Exception as e:
        logger.error(f"Error sending due date reminders: {e}")

