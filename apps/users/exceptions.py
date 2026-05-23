"""Custom exceptions and exception handler."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    """Custom DRF exception handler."""
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': _get_error_message(response.data),
                'details': response.data,
            }
        }
        response.data = error_data
    else:
        logger.exception(f"Unhandled exception in {context.get('view', 'unknown')}: {exc}")
        response = Response(
            {
                'success': False,
                'error': {
                    'status_code': 500,
                    'message': 'Internal server error',
                    'details': str(exc),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response


def _get_error_message(data):
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        if 'non_field_errors' in data:
            return str(data['non_field_errors'][0])
        first_key = next(iter(data))
        return f"{first_key}: {data[first_key][0] if isinstance(data[first_key], list) else data[first_key]}"
    if isinstance(data, list):
        return str(data[0])
    return str(data)


class TelegramAuthError(Exception):
    """Raised when Telegram authentication fails."""
    pass


class SubscriptionRequired(Exception):
    """Raised when user hasn't subscribed to required channels."""
    pass


class PremiumRequired(Exception):
    """Raised when a premium feature is accessed by free user."""
    pass


class AILimitExceeded(Exception):
    """Raised when user exceeds AI usage limit."""
    pass
