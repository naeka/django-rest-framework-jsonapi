from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

from tests.models import Person, Comment


pytestmark = pytest.mark.django_db


def test_one_person(client):
    Person.objects.create(last_name="Davis", first_name="Molly")
    response = client.get(reverse("person-list"))
    assert json.loads(response.content.decode()) == {
        "data": [
            {
                "id": "1",
                "type": "persons",
                "attributes": {
                    "first-name": "Molly",
                    "last-name": "Davis",
                    "twitter": ""
                }
            }
        ]
    }


def test_more_persons(client):
    Person.objects.create(last_name="Davis", first_name="Molly")
    Person.objects.create(last_name="Lightyear", first_name="Buzz")
    response = client.get(reverse("person-list"))
    assert json.loads(response.content.decode()) == {
        "data": [
            {
                "id": "1",
                "type": "persons",
                "attributes": {
                    "first-name": "Molly",
                    "last-name": "Davis",
                    "twitter": ""
                }
            },
            {
                "id": "2",
                "type": "persons",
                "attributes": {
                    "first-name": "Buzz",
                    "last-name": "Lightyear",
                    "twitter": ""
                }
            }
        ]
    }


def test_one_comment_with_sideloaded_author(client):
    author = Person.objects.create(last_name="Davis", first_name="Molly")
    Comment.objects.create(body="Molly's comment", author=author)
    response = client.get("{}?include=author".format(reverse("comment-list")))
    assert json.loads(response.content.decode()) == {
        "data": [
            {
                "id": "1",
                "type": "comments",
                "attributes": {
                    "body": "Molly's comment"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "1",
                            "type": "persons"
                        }
                    }
                }
            }
        ],
        "included": [
            {
                "id": "1",
                "type": "persons",
                "attributes": {
                    "first-name": "Molly",
                    "last-name": "Davis",
                    "twitter": ""
                }
            }
        ]
    }


def test_more_comments_with_sideloaded_authors(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    Comment.objects.create(body="Molly's comment", author=molly)
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    response = client.get("{}?include=author".format(reverse("comment-list")))
    assert json.loads(response.content.decode()) == {
        "data": [
            {
                "id": "1",
                "type": "comments",
                "attributes": {
                    "body": "Molly's comment"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "1",
                            "type": "persons"
                        }
                    }
                }
            },
            {
                "id": "2",
                "type": "comments",
                "attributes": {
                    "body": "Buzz' comment"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "2",
                            "type": "persons"
                        }
                    }
                }
            }
        ],
        "included": [
            {
                "id": "1",
                "type": "persons",
                "attributes": {
                    "first-name": "Molly",
                    "last-name": "Davis",
                    "twitter": ""
                }
            },
            {
                "id": "2",
                "type": "persons",
                "attributes": {
                    "first-name": "Buzz",
                    "last-name": "Lightyear",
                    "twitter": ""
                }
            }
        ]
    }
