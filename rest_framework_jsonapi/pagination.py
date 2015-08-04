from __future__ import unicode_literals

from rest_framework.response import Response
from rest_framework.compat import OrderedDict
from rest_framework.utils.urls import remove_query_param, replace_query_param
from rest_framework.pagination import (
    PageNumberPagination as DrfPageNumberPagination,
    LimitOffsetPagination as DrfLimitOffsetPagination,
    CursorPagination as DrfCursorPagination
)


class PageNumberPagination(DrfPageNumberPagination):
    page_query_param = "page[number]"

    def get_first_link(self):
        url = self.request.build_absolute_uri()
        return remove_query_param(url, self.page_query_param)

    def get_last_link(self):
        url = self.request.build_absolute_uri()
        page_number = self.page.paginator.num_pages
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        prev_link = self.get_previous_link()
        next_link = self.get_next_link()
        if not prev_link and not next_link:
            return Response(data)
        return Response(OrderedDict([
            ("links", OrderedDict([
                ("first", self.get_first_link()),
                ("last", self.get_last_link()),
                ("prev", prev_link),
                ("next", next_link)])),
            ("meta", OrderedDict([
                ("count", self.page.paginator.count)])),
            ("data", data)
        ]))


class LimitOffsetPagination(DrfLimitOffsetPagination):
    limit_query_param = "page[limit]"
    offset_query_param = "page[offset]"

    def get_paginated_response(self, data):
        prev_link = self.get_previous_link()
        next_link = self.get_next_link()
        if not prev_link and not next_link:
            return Response(data)
        return Response(OrderedDict([
            ("links", OrderedDict([
                ("prev", prev_link),
                ("next", next_link)])),
            ("meta", OrderedDict([
                ("count", self.count)])),
            ("data", data)
        ]))


class CursorPagination(DrfCursorPagination):
    cursor_query_param = "page[cursor]"
    ordering = "id"

    def get_paginated_response(self, data):
        prev_link = self.get_previous_link()
        next_link = self.get_next_link()
        if not prev_link and not next_link:
            return Response(data)
        return Response(OrderedDict([
            ("links", OrderedDict([
                ("prev", prev_link),
                ("next", next_link)])),
            ("data", data)
        ]))
