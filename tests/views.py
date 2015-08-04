from rest_framework import viewsets
from rest_framework_jsonapi.pagination import (
    PageNumberPagination, LimitOffsetPagination, CursorPagination)
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


from tests.models import Article, Person, Comment
from tests.serializers import (ArticleSerializer, PersonSerializer,
                               CommentSerializer, OnlyCommentSerializer)


class Articles(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = PageNumberPagination


class People(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    pagination_class = LimitOffsetPagination


class Comments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CursorPagination


class OnlyComments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = OnlyCommentSerializer


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
