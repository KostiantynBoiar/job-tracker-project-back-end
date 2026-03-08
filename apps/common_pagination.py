from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Standard pagination class for list endpoints.
    
    Query parameters:
        - page: Page number (default: 1)
        - page_size: Number of items per page (default: 20, max: 100)
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
