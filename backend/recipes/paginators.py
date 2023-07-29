from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    limit = 6
    page_size_query_param = "limit"
