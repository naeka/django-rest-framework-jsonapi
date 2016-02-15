from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

from tests.models import Person, Comment


pytestmark = pytest.mark.django_db


def obvious_resource_type(model):
    return 'object'


def test_valid_get_resource_type(client, settings):
    settings.REST_FRAMEWORK.update(
        RESOURCE_TYPE_EXTRACTOR="tests.test_utils.obvious_resource_type")
    Person.objects.create(last_name="Davis", first_name="Molly")
    response = client.get(reverse("person-detail", args=[1]))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "object",
            "attributes": {
                "first-name": "Molly",
                "last-name": "Davis",
                "twitter": ""
            }
        }
    }
    settings.REST_FRAMEWORK.pop("RESOURCE_TYPE_EXTRACTOR")


def test_invalid_get_resource_type(client, settings):
    settings.REST_FRAMEWORK.update(
        RESOURCE_TYPE_EXTRACTOR="tests.test_utils.noop")
    Person.objects.create(last_name="Davis", first_name="Molly")
    with pytest.raises(ImportError):
        client.get(reverse("person-detail", args=[1]))
    settings.REST_FRAMEWORK.pop("RESOURCE_TYPE_EXTRACTOR")


def test_valid_import_serializer(client, settings):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    response = client.get(reverse("valid-lazy-comment-detail", args=[1]))
    assert response.status_code is 200


def test_invalid_import_serializer(client, settings):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    with pytest.raises(ImportError):
        client.get(reverse("invalid-lazy-comment-detail", args=[1]))
