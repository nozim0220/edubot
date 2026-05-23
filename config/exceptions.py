"""Custom exception handler for EduBot API."""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    """Custom exception handler - consistent JSON error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'status_code': response.status_code,
            'errors': response.data,
        }
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_data['message'] = str(response.data['detail'])
            else:
                error_data['message'] = 'Validation error'
        elif isinstance(response.data, list):
            error_data['message'] = str(response.data[0]) if response.data else 'Error'
        response.data = error_data
        return response

    if isinstance(exc, ValidationError):
        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Validation error',
            'errors': exc.message_dict if hasattr(exc, 'message_dict') else {'detail': exc.messages},
        }, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, Http404):
        return Response({
            'success': False,
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': 'Resource not found',
            'errors': {'detail': 'Not found.'},
        }, status=status.HTTP_404_NOT_FOUND)

    logger.error(f'Unhandled exception: {exc}', exc_info=True)
    return Response({
        'success': False,
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'message': 'Internal server error',
        'errors': {'detail': 'An unexpected error occurred.'},
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
