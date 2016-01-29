from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

from tests.models import Person, Comment, FormattingWithABBR


pytestmark = pytest.mark.django_db


def test_type_formatting(client):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    comment = Comment.objects.create(body="Buzz' comment", author=buzz)
    FormattingWithABBR.objects.create(unique_comment=comment)
    response = client.get(reverse("formatting-detail", args=[1]))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "formatting-with-abbr",
            "relationships": {
                "unique-comment": {
                    "data": {
                        "id": "1",
                        "type": "comment"
                    }
                }
            }
        }
    }


def test_included_query_argument_formatting(client):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    comment = Comment.objects.create(body="Buzz' comment", author=buzz)
    FormattingWithABBR.objects.create(unique_comment=comment)
    response = client.get("{}?include=unique-comment".format(
        reverse("formatting-detail", args=[1])))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "formatting-with-abbr",
            "relationships": {
                "unique-comment": {
                    "data": {
                        "id": "1",
                        "type": "comment"
                    }
                }
            }
        },
        "included": [
            {
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
        ]
    }
