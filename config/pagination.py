"""Custom pagination classes for EduBot API."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination - 20 items per page."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'count': {'type': 'integer'},
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'total_pages': {'type': 'integer'},
                'current_page': {'type': 'integer'},
                'results': schema,
            }
        }


class LargeResultsSetPagination(PageNumberPagination):
    """Larger pagination for admin endpoints."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """Small pagination for quick lists."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
