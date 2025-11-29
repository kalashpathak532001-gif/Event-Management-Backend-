import logging
from typing import Iterable, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from .models import Event

User = get_user_model()
logger = logging.getLogger(__name__)


def _get_sender_email() -> Optional[str]:
    host_user = getattr(settings, 'EMAIL_HOST_USER', '')
    host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', host_user)
    if not (host_user and host_password and from_email):
        logger.info("Email not configured; skipping notification dispatch.")
        return None
    return from_email


def _get_recipients(exclude: Optional[Iterable[str]] = None) -> list[str]:
    exclusion_set = set(email.lower() for email in exclude or [] if email)
    recipients = [
        email for email in User.objects.exclude(email='').values_list('email', flat=True)
        if email.lower() not in exclusion_set
    ]
    return recipients


def _format_event_datetime(event: Event) -> str:
    event_dt = event.event_date
    if timezone.is_naive(event_dt):
        event_dt = timezone.make_aware(event_dt, timezone.get_current_timezone())
    event_dt = timezone.localtime(event_dt)
    return event_dt.strftime('%A, %d %B %Y at %H:%M %Z')


def _dispatch_event_email(subject: str, message: str, exclude: Optional[Iterable[str]] = None) -> int:
    sender = _get_sender_email()
    if not sender:
        return 0

    recipients = _get_recipients(exclude=exclude)
    if not recipients:
        logger.info("No recipients available for event notification.")
        return 0

    try:
        return send_mail(
            subject=subject,
            message=message,
            from_email=sender,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception as exc:  # pragma: no cover - best effort notification
        logger.warning("Failed to send event notification: %s", exc)
        return 0


def send_event_created_notification(event: Event) -> int:
    event_dt = _format_event_datetime(event)
    creator_name = event.created_by.get_full_name() or event.created_by.email
    subject = f"New event scheduled: {event.title}"
    message = (
        f"A new event has been scheduled by {creator_name}.\n\n"
        f"Title: {event.title}\n"
        f"When: {event_dt}\n"
        f"Description: {event.description or 'No description provided.'}\n\n"
        "Log in to PlanSync for more details."
    )
    return _dispatch_event_email(subject, message, exclude=[event.created_by.email])


def send_event_manual_reminder(event: Event, triggered_by) -> int:
    event_dt = _format_event_datetime(event)
    trigger_name = triggered_by.get_full_name() or triggered_by.email
    subject = f"Reminder: {event.title} on {event_dt}"
    message = (
        f"{trigger_name} sent a reminder for the upcoming event.\n\n"
        f"Title: {event.title}\n"
        f"When: {event_dt}\n"
        f"Description: {event.description or 'No description provided.'}\n\n"
        "Please confirm your availability in PlanSync."
    )
    # Do not exclude the trigger—they likely expect the reminder too.
    return _dispatch_event_email(subject, message)


