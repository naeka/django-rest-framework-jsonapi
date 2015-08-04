from __future__ import unicode_literals

from django.core.urlresolvers import reverse


def test_request(client):
    response = client.options(reverse("person-list"))
    assert response["Content-Type"] == "application/vnd.api+json"
