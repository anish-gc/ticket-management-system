from django.db.models import Q, Case, When, IntegerField, F
from django.utils import timezone
from datetime import timedelta
from typing import Optional, List, Dict, Any


class TicketFilterManager:
    """
    Centralized ticket filtering and ordering system for ticket management
    """

    @staticmethod
    def get_filtered_tickets(
        menu=None,
        status_codes: Optional[List[str]] = None,
        priority_codes: Optional[List[str]] = None,
        sla_breached: Optional[bool] = None,
        response_overdue: Optional[bool] = None,
        escalated: Optional[bool] = None,
        assigned_to=None,
        created_for=None,
        days_old: Optional[int] = None,
        order_by: str = "importance",  # 'importance', 'created', 'deadline', 'sla'
    ):
        """
        Get filtered and ordered ticket queryset

        Args:
            menu: Menu instance to filter by
            status_codes: List of status codes to filter by
            priority_codes: List of priority codes to filter by
            sla_breached: Filter by SLA breach status
            response_overdue: Filter tickets with overdue response deadline
            escalated: Filter by escalation status
            assigned_to: Account instance for assignee filter
            created_for: Account instance for creator filter
            days_old: Filter tickets older than X days
            order_by: Ordering strategy

        Returns:
            QuerySet: Filtered and ordered ticket queryset
        """
        from tickets.models import Ticket

        # Base queryset with related data
        queryset = Ticket.objects.select_related(
            "status", "priority", "menu", "assigned_to", "created_for"
        ).filter(is_active=True)

        # Menu filtering (for reuse in menu-specific views)
        if menu:
            queryset = queryset.filter(menu=menu)

        # Status filtering
        if status_codes:
            queryset = queryset.filter(status__code__in=status_codes)

        # Priority filtering
        if priority_codes:
            queryset = queryset.filter(priority__code__in=priority_codes)

        # SLA breach filtering
        if sla_breached is not None:
            queryset = queryset.filter(sla_breached=sla_breached)

        # Response overdue filtering
        if response_overdue is not None:
            now = timezone.now()
            if response_overdue:
                queryset = queryset.filter(
                    response_deadline__lt=now, first_response_at__isnull=True
                )
            else:
                queryset = queryset.filter(
                    Q(response_deadline__gte=now) | Q(first_response_at__isnull=False)
                )

        # Escalation filtering
        if escalated is not None:
            queryset = queryset.filter(is_escalated=escalated)

        # Assignee filtering
        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)

        # Creator filtering
        if created_for:
            queryset = queryset.filter(created_for=created_for)

        # Age filtering
        if days_old:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            queryset = queryset.filter(created_at__lt=cutoff_date)

        # Apply ordering
        return TicketFilterManager._apply_ordering(queryset, order_by)

    @staticmethod
    def _apply_ordering(queryset, order_by: str):
        """Apply ordering strategy to queryset"""

        if order_by == "importance":
            # Smart importance-based ordering
            return queryset.annotate(
                # Calculate urgency score
                urgency_score=Case(
                    # SLA breached = highest urgency
                    When(sla_breached=True, then=1000),
                    # Response overdue
                    When(
                        response_deadline__lt=timezone.now(),
                        first_response_at__isnull=True,
                        then=800,
                    ),
                    # Escalated tickets
                    When(is_escalated=True, then=600),
                    # SLA approaching (within 2 hours)
                    When(
                        sla_due_date__lt=timezone.now() + timedelta(hours=2),
                        sla_due_date__gt=timezone.now(),
                        then=400,
                    ),
                    # Default: use priority weight
                    default=F("priority__weight"),
                    output_field=IntegerField(),
                )
            ).order_by(
                "-urgency_score",  # Higher urgency first
                "status__weight",  # Lower status weight = higher priority
                "sla_due_date",  # Earlier SLA first
                "created_at",  # Older tickets first
            )

        elif order_by == "sla":
            # SLA-focused ordering
            return queryset.order_by(
                "-sla_breached",  # Breached first
                "sla_due_date",  # Earliest SLA first
                "-priority__weight",  # High priority first
                "created_at",
            )

        elif order_by == "deadline":
            # Deadline-focused ordering
            return queryset.order_by(
                "response_deadline",  # Earliest deadline first
                "due_date",
                "-priority__weight",
                "created_at",
            )

        elif order_by == "created":
            # Creation time ordering
            return queryset.order_by("-created_at")

        elif order_by == "priority":
            # Priority-focused ordering
            return queryset.order_by(
                "-priority__weight",  # High priority first
                "status__weight",  # Low status weight first
                "created_at",
            )

        else:
            # Default to importance
            return TicketFilterManager._apply_ordering(queryset, "importance")

    @staticmethod
    def get_dashboard_tickets(user, limit: int = 10):
        """
        Get prioritized tickets for dashboard view

        Args:
            user: Current user (Account instance)
            limit: Maximum number of tickets to return

        Returns:
            Dict: Categorized tickets for dashboard
        """
        base_filters = {
            "status_codes": ["OPEN", "IN_PROGRESS", "PENDING"],  # Active statuses
            "order_by": "importance",
        }

        # User-specific filters based on role
        if hasattr(user, "role"):
            if user.role == "agent":
                assigned_tickets = TicketFilterManager.get_filtered_tickets(
                    assigned_to=user, **base_filters
                )[:limit]
            elif user.role == "supervisor":
                # Supervisors see escalated and high-priority tickets
                assigned_tickets = TicketFilterManager.get_filtered_tickets(
                    assigned_to=user, **base_filters
                )[: limit // 2]

                escalated_tickets = TicketFilterManager.get_filtered_tickets(
                    escalated=True, **base_filters
                )[: limit // 2]

                return {
                    "assigned": assigned_tickets,
                    "escalated": escalated_tickets,
                    "sla_breached": TicketFilterManager.get_filtered_tickets(
                        sla_breached=True, **base_filters
                    )[:5],
                }
            else:
                # Admin or other roles see all critical tickets
                assigned_tickets = TicketFilterManager.get_filtered_tickets(
                    **base_filters
                )[:limit]
        else:
            assigned_tickets = TicketFilterManager.get_filtered_tickets(**base_filters)[
                :limit
            ]

        return {
            "my_tickets": assigned_tickets,
            "urgent": TicketFilterManager.get_filtered_tickets(
                sla_breached=True,
                escalated=True,
                **{k: v for k, v in base_filters.items() if k != "assigned_to"}
            )[:5],
        }
