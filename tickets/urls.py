from django.urls import path

from tickets.views.notification_log_views import (
    NotificationLogDetailsApiView,
    NotificationLogsListApiView,
)
from tickets.views.ticket_priority_views import (
    TicketPriorityCreateListApiView,
    TicketPriorityDetailsApiView,
)
from tickets.views.ticket_status_views import (
    TicketStatusCreateListApiView,
    TicketStatusDetailsApiView,
)
from tickets.views.ticket_views import TicketCreateListApiView, TicketDetailsApiView


urlpatterns = [
    # tickets
    path("tickets/", TicketCreateListApiView.as_view(), name="ticket-create-list"),
    path("ticket/<pk>/", TicketDetailsApiView.as_view(), name="ticket-details"),
    # ticket-priority
    path(
        "ticket-priority/",
        TicketPriorityCreateListApiView.as_view(),
        name="ticket-priority-create-list",
    ),
    path(
        "ticket-priority/<pk>/",
        TicketPriorityDetailsApiView.as_view(),
        name="ticket-priority-details",
    ),
    # ticket-status
    path(
        "ticket-status/",
        TicketStatusCreateListApiView.as_view(),
        name="ticket-status-create-list",
    ),
    path(
        "ticket-status/<pk>/",
        TicketStatusDetailsApiView.as_view(),
        name="ticket-status-details",
    ),
    path(
        "tickets/notification-logs/",
        NotificationLogsListApiView.as_view(),
        name="ticket-notification-logs-list",
    ),
    path(
        "tickets/notification-log/<pk>/",
        NotificationLogDetailsApiView.as_view(),
        name="ticket-notification-log-details",
    ),
]
