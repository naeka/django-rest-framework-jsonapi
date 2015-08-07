from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

from tests.models import Article, Person, Comment


pytestmark = pytest.mark.django_db


def test_person(client):
    response = client.post(reverse("person-list"), data=json.dumps({
        "data": {
            "type": "person",
            "attributes": {
                "first-name": "Molly",
                "last-name": "Davis",
                "twitter": ""
            }
        }
    }), content_type="application/vnd.api+json")

    assert response.status_code == 201
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
    assert response["content-type"] == "application/vnd.api+json"
    person = Person.objects.first()
    assert person.last_name == "Davis"


def test_article(client):
    Person.objects.create(last_name="Davis", first_name="Molly")
    author = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=author)
    response = client.post(reverse("article-list"), data=json.dumps({
        "data": {
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
    }), content_type="application/vnd.api+json")

    assert response.status_code == 201
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
    assert response["content-type"] == "application/vnd.api+json"
    article = Article.objects.first()
    assert article.title == "Molly's article"
    assert article.comments.first().author.last_name == "Lightyear"
