# tickets/utils/email_utils.py
import logging
import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger("django")


def send_ticket_notification_email(
    user, notification_type, ticket, changes=None, **extra_data
):
    """
    Sends a ticket notification email to the user based on notification type.

    Args:
        user: User object receiving the notification
        notification_type: Type of notification (created, assigned, updated, etc.)
        ticket: Ticket instance
        changes: List of changes made to the ticket (for update notifications)
        **extra_data: Additional data to pass to the template
    """

    # Define notification configurations
    notification_configs = {
        "ticket_created": {
            "subject": f"New Ticket Created: {ticket.title}",
            "icon": "🎫",
            "title": "New Ticket Created",
            "message": f"A new support ticket has been created and requires attention.",
        },
        "ticket_assigned": {
            "subject": f"Ticket Assigned to You: {ticket.title}",
            "icon": "👤",
            "title": "Ticket Assigned",
            "message": f"You have been assigned to work on this ticket.",
        },
        "ticket_reassigned": {
            "subject": f"Ticket Reassigned: {ticket.title}",
            "icon": "🔄",
            "title": "Ticket Reassigned",
            "message": f"This ticket has been reassigned.",
        },
        "ticket_updated": {
            "subject": f"Ticket Updated: {ticket.title}",
            "icon": "📝",
            "title": "Ticket Updated",
            "message": f"This ticket has been updated with new information.",
        },
        "status_changed": {
            "subject": f"Ticket Status Changed: {ticket.title}",
            "icon": "🔄",
            "title": "Status Changed",
            "message": f"The status of this ticket has been changed.",
        },
        "priority_changed": {
            "subject": f"Ticket Priority Changed: {ticket.title}",
            "icon": "⚡",
            "title": "Priority Changed",
            "message": f"The priority level of this ticket has been updated.",
        },
        "due_date_approaching": {
            "subject": f"Due Date Approaching: {ticket.title}",
            "icon": "⏰",
            "title": "Due Date Approaching",
            "message": f"This ticket is approaching its due date and needs attention.",
        },
    }

    config = notification_configs.get(
        notification_type,
        {
            "subject": f"Ticket Notification: {ticket.title}",
            "icon": "📋",
            "title": "Ticket Notification",
            "message": "This ticket has been updated.",
        },
    )

    # Generate URLs (adjust these based on your URL patterns)
    try:
        ticket_url = settings.SITE_URL + reverse(
            "ticket_detail", kwargs={"reference_id": ticket.reference_id}
        )

    except:
        # Fallback URLs if reverse fails
        base_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        ticket_url = f"{base_url}/tickets/{ticket.reference_id}/"

    # Prepare template context
    context = {
        "username": user.username or user.email,
        "ticket": ticket,
        "notification_icon": config["icon"],
        "notification_title": config["title"],
        "notification_message": config["message"],
        "changes": changes,
        "ticket_url": ticket_url,
        "company_name": getattr(settings, "COMPANY_NAME", "Your Company"),
        "current_date": timezone.now().strftime("%B %d, %Y at %I:%M %p"),
        **extra_data,
    }

    from_email = settings.DEFAULT_FROM_EMAIL or "anishgharti10@gmail.com"
    to_email = user.email
    subject = config["subject"]

    # Render the email template
    try:
        html_message = render_to_string("emails/ticket_notification.html", context)

        mail = EmailMessage(subject, html_message, from_email, to=[to_email])
        mail.content_subtype = "html"

        mail.send()
        logger.info(
            f"Ticket notification email sent to {to_email} for {notification_type}"
        )
        return True

    except Exception as e:
        logger.error(
            f"Failed to send ticket notification email to {to_email} for {notification_type}",
            exc_info=True,
        )
        return False
