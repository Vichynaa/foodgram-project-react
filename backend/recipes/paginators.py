from rest_framework.pagination import PageNumberPagination
from foodgram.settings import PAGE_LIMIT


class PageLimitPagination(PageNumberPagination):
    limit = PAGE_LIMIT
    page_size_query_param = "limit"
