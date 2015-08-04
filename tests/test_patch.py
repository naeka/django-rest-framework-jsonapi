from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils import six

import json
import pytest

from tests.models import Article, Person, Comment


pytestmark = pytest.mark.django_db


def test_article(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    comment_1 = Comment.objects.create(body="Buzz' comment", author=buzz)
    Comment.objects.create(body="Buzz' other comment", author=buzz)
    article = Article.objects.create(title="Molly's article", author=molly)
    article.comments.add(comment_1)
    response = client.patch(
        reverse("article-detail", args=[article.id]), data=json.dumps({
            "data": {
                "id": six.text_type(article.id),
                "type": "articles",
                "attributes": {
                    "title": "Molly's updated article"
                },
                "relationships": {
                    "comments": {
                        "data": [
                            {"id": "1", "type": "comments"},
                            {"id": "2", "type": "comments"}
                        ]
                    }
                }
            }
        }), content_type="application/vnd.api+json")

    assert response.status_code == 200
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "articles",
            "attributes": {
                "title": "Molly's updated article"
            },
            "relationships": {
                "author": {
                    "data": {"id": "1", "type": "persons"}
                },
                "comments": {
                    "data": [
                        {"id": "1", "type": "comments"},
                        {"id": "2", "type": "comments"}
                    ]
                }
            }
        }
    }
    assert response["content-type"] == "application/vnd.api+json"
    article = Article.objects.first()
    assert article.title == "Molly's updated article"
    assert article.comments.first().author.last_name == "Lightyear"
    assert article.comments.count() is 2
