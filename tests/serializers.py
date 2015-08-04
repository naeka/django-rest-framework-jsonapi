from __future__ import unicode_literals

from rest_framework import serializers
from tests.models import Article, Person, Comment


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
