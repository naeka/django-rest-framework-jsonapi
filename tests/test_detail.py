from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

from tests.models import Article, Person, Comment


pytestmark = pytest.mark.django_db


def test_person(client):
    Person.objects.create(last_name="Davis", first_name="Molly")
    response = client.get(reverse("person-detail", args=[1]))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "person",
            "attributes": {
                "first-name": "Molly",
                "last-name": "Davis",
                "twitter": ""
            }
        }
    }


def test_article(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    comment = Comment.objects.create(body="Buzz' comment", author=buzz)
    article = Article.objects.create(title="Molly's article", author=molly)
    article.comments.add(comment)
    response = client.get(reverse("article-detail", args=[1]))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "article",
            "attributes": {
                "title": "Molly's article"
            },
            "relationships": {
                "author": {
                    "data": {"id": "1", "type": "person"}
                },
                "comments": {
                    "data": [
                        {"id": "1", "type": "comment"}
                    ]
                }
            }
        }
    }


def test_article_with_sideloaded_data(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    comment = Comment.objects.create(body="Buzz' comment", author=buzz)
    article = Article.objects.create(title="Molly's article", author=molly)
    article.comments.add(comment)
    response = client.get("{}?include=author,comments".format(
        reverse("article-detail", args=[1])))

    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "article",
            "attributes": {
                "title": "Molly's article"
            },
            "relationships": {
                "author": {
                    "data": {"id": "1", "type": "person"}
                },
                "comments": {
                    "data": [
                        {"id": "1", "type": "comment"}
                    ]
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "person",
                "attributes": {
                    "first-name": "Molly",
                    "last-name": "Davis",
                    "twitter": ""
                }
            },
            {
                "id": "1",
                "type": "comment",
                "attributes": {
                    "body": "Buzz' comment"
                },
                "relationships": {
                    "author": {
                        "data": {"id": "2", "type": "person"}
                    }
                }
            }
        ]
    }


def test_article_with_nested_sideloaded_data(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    comment = Comment.objects.create(body="Buzz' comment", author=buzz)
    article = Article.objects.create(title="Molly's article", author=molly)
    article.comments.add(comment)
    response = client.get("{}?include=author,comments,comments.author".format(
        reverse("article-detail", args=[1])))

    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "article",
            "attributes": {
                "title": "Molly's article"
            },
            "relationships": {
                "author": {
                    "data": {"id": "1", "type": "person"}
                },
                "comments": {
                    "data": [
                        {"id": "1", "type": "comment"}
                    ]
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "person",
                "attributes": {
                    "first-name": "Molly",
                    "last-name": "Davis",
                    "twitter": ""
                }
            },
            {
                "id": "1",
                "type": "comment",
                "attributes": {
                    "body": "Buzz' comment"
                },
                "relationships": {
                    "author": {
                        "data": {"id": "2", "type": "person"}
                    }
                }
            },
            {
                "id": "2",
                "type": "person",
                "attributes": {
                    "first-name": "Buzz",
                    "last-name": "Lightyear",
                    "twitter": ""
                }
            }
        ]
    }


def test_comment_with_sideloaded_data_and_include_missing_in_meta(client):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    response = client.get("{}?include=author".format(
        reverse("only-comment-detail", args=[1])))

    # Can't determine nested serializer.
    # Thus should not have the included person.
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "comment",
            "attributes": {
                "body": "Buzz' comment"
            },
            "relationships": {
                "author": {
                    "data": {
                        "id": "1",
                        "type": "person"
                    }
                }
            }
        }
    }


def test_comment_with_sideloaded_data_and_read_only_author(client):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    response = client.get("{}?include=author".format(
        reverse("read-only-author-comment-detail", args=[1])))

    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "comment",
            "attributes": {
                "body": "Buzz' comment"
            },
            "relationships": {
                "author": {
                    "data": {
                        "id": "1",
                        "type": "person"
                    }
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "person",
                "attributes": {
                    "first-name": "Buzz",
                    "last-name": "Lightyear",
                    "twitter": ""
                }
            }
        ]
    }
