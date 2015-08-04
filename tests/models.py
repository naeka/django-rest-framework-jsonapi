from django.db import models


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
