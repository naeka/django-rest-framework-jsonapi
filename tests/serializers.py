from __future__ import unicode_literals

from rest_framework import serializers
from tests.models import Article, Person, Comment, TestFormattingWithABBR


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        include = {
            "author": PersonSerializer(),
        }


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        include = {
            "author": PersonSerializer(),
            "comments": CommentSerializer(),
        }


class OnlyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment


class ImproperlyConfiguredReadOnlyAuthorCommentSerializer(
        serializers.ModelSerializer):
    class Meta:
        model = Comment
        read_only_fields = ("author",)
        include = {
            "author": PersonSerializer(),
        }


class ReadOnlyAuthorCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        read_only_fields = ("author",)
        include = {
            "author": PersonSerializer(),
        }
        model_map = {
            "author": Person,
        }


class TestFormattingWithABBRSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFormattingWithABBR
        include = {
            "unique_comment": CommentSerializer(),
        }
