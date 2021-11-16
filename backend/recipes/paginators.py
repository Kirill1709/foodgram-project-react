from rest_framework.pagination import PageNumberPagination


class PageNumberPaginatorCustom(PageNumberPagination):
    page_size_query_param = 'limit'
