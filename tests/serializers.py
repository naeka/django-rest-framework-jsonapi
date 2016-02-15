from __future__ import unicode_literals

from rest_framework_jsonapi.serializers import JsonApiSerializer
from tests.models import (
    Article, Person, Comment, FormattingWithABBR, Individual, BaseOrganization,
    Company, Association)


class PersonSerializer(JsonApiSerializer):
    class Meta:
        model = Person


class CommentSerializer(JsonApiSerializer):
    class Meta:
        model = Comment
        include = {
            "author": PersonSerializer(),
        }


class OnlyCommentSerializer(JsonApiSerializer):
    class Meta:
        model = Comment


class ValidLazyCommentSerializer(JsonApiSerializer):
    class Meta:
        model = Comment
        include = {
            "author": "tests.serializers.PersonSerializer",
        }


class InvalidLazyCommentSerializer(JsonApiSerializer):
    class Meta:
        model = Comment
        include = {
            "author": "tests.serializers.InvalidPersonSerializer",
        }


class ArticleSerializer(JsonApiSerializer):
    class Meta:
        model = Article
        include = {
            "author": PersonSerializer(),
            "comments": CommentSerializer(),
        }


class ImproperlyConfiguredReadOnlyAuthorCommentSerializer(
        JsonApiSerializer):
    class Meta:
        model = Comment
        read_only_fields = ("author",)
        include = {
            "author": PersonSerializer(),
        }


class ReadOnlyAuthorCommentSerializer(JsonApiSerializer):
    class Meta:
        model = Comment
        read_only_fields = ("author",)
        include = {
            "author": PersonSerializer(),
        }


class FormattingWithABBRSerializer(JsonApiSerializer):
    class Meta:
        model = FormattingWithABBR
        include = {
            "unique_comment": CommentSerializer(),
        }


class CompanySerializer(JsonApiSerializer):
    class Meta:
        model = Company
        exclude = ('polymorphic_ctype',)


class AssociationSerializer(JsonApiSerializer):
    class Meta:
        model = Association
        exclude = ('polymorphic_ctype',)


class OrganizationSerializer(JsonApiSerializer):
    class Meta:
        model = BaseOrganization
        exclude = ('polymorphic_ctype',)

    def to_representation(self, instance):
        # Handle polymorphism
        if isinstance(instance, Company):
            return CompanySerializer(
                instance, context=self.context).to_representation(instance)
        elif isinstance(instance, Association):
            return AssociationSerializer(
                instance, context=self.context).to_representation(instance)
        return super(OrganizationSerializer, self).to_representation(instance)


class IndividualSerializer(JsonApiSerializer):
    class Meta:
        model = Individual
        include = {
            "organization": OrganizationSerializer(),
            "other_organizations": OrganizationSerializer(),
        }
