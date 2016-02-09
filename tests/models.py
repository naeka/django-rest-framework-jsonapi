from django.db import models
from polymorphic.models import PolymorphicModel


class Person(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    twitter = models.CharField(max_length=64, blank=True)


class Comment(models.Model):
    body = models.TextField(max_length=2048)
    author = models.ForeignKey(Person)


class Article(models.Model):
    title = models.CharField(max_length=64)
    author = models.ForeignKey(Person)
    comments = models.ManyToManyField(Comment)


class FormattingWithABBR(models.Model):
    unique_comment = models.ForeignKey(Comment)


class BaseOrganization(PolymorphicModel):
    name = models.CharField(max_length=128)


class Company(BaseOrganization):
    pass


class Association(BaseOrganization):
    pass


class Individual(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    organization = models.ForeignKey('BaseOrganization', null=True, blank=True)
    other_organizations = models.ManyToManyField(
        'BaseOrganization', null=True, blank=True)
