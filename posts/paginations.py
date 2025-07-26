from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PostPagination(PageNumberPagination):
    max_page_size = 100
    page_size = 10
    page_size_query_param = 'set_size' # for test

    def get_paginated_response(self, data):
        return Response({
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'count': self.page.paginator.count,
            'resutls': data
        })