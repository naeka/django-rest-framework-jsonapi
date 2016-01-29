from rest_framework import viewsets, permissions
from rest_framework_jsonapi.pagination import (
    PageNumberPagination, LimitOffsetPagination, CursorPagination)
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


from tests.models import Article, Person, Comment, FormattingWithABBR
from tests.serializers import (
    ArticleSerializer, PersonSerializer, CommentSerializer,
    ImproperlyConfiguredReadOnlyAuthorCommentSerializer,
    ReadOnlyAuthorCommentSerializer, OnlyCommentSerializer,
    FormattingWithABBRSerializer)


class DenyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return False


class Articles(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = PageNumberPagination


class People(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    pagination_class = LimitOffsetPagination


class AuthenticatedPeople(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (DenyPermission,)


class Comments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CursorPagination


class OnlyComments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = OnlyCommentSerializer


class ImproperlyConfiguredReadOnlyAuthorComments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = ImproperlyConfiguredReadOnlyAuthorCommentSerializer


class ReadOnlyAuthorComments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = ReadOnlyAuthorCommentSerializer


class FormattingWithABBRs(viewsets.ModelViewSet):
    queryset = FormattingWithABBR.objects.all()
    serializer_class = FormattingWithABBRSerializer


class AnonImmediateRateThrottle(AnonRateThrottle):
    rate = '0/sec'
    scope = 'seconds'


@api_view()
@throttle_classes([AnonImmediateRateThrottle])
def throttled_view(request):
    return Response("Throttled")


@api_view()
def validation_error_view(request):
    raise ValidationError("Validation error")


@api_view()
def errored_view(request):
    raise NotImplementedError("Errored view")
