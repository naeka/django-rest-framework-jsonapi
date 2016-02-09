from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

from tests.models import Individual, Company, Association


pytestmark = pytest.mark.django_db


def test_person(client):
    company1_obj = Company.objects.create(name='Company 1')
    company2_obj = Company.objects.create(name='Company 2')
    association_obj = Association.objects.create(name='Association')
    individual_obj = Individual.objects.create(
        last_name="Davis", first_name="Molly", organization=company1_obj)
    individual_obj.other_organizations.add(company2_obj, association_obj)
    response = client.get(
        reverse("individual-detail", args=[individual_obj.pk]))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "individual",
            "attributes": {
                "first-name": "Molly",
                "last-name": "Davis"
            },
            "relationships": {
                "organization": {
                    "data": {"id": "1", "type": "company"}
                },
                "other-organizations": {
                    "data": [
                        {"id": "2", "type": "company"},
                        {"id": "3", "type": "association"}
                    ]
                }
            }
        }
    }


def test_person_with_sideloaded_data(client):
    company1_obj = Company.objects.create(name='Company 1')
    company2_obj = Company.objects.create(name='Company 2')
    association_obj = Association.objects.create(name='Association')
    individual_obj = Individual.objects.create(
        last_name="Davis", first_name="Molly", organization=company1_obj)
    individual_obj.other_organizations.add(company2_obj, association_obj)
    response = client.get("{}?include=organization,other-organizations".format(
        reverse("individual-detail", args=[individual_obj.pk])))
    assert json.loads(response.content.decode()) == {
        "data": {
            "id": "1",
            "type": "individual",
            "attributes": {
                "first-name": "Molly",
                "last-name": "Davis"
            },
            "relationships": {
                "organization": {
                    "data": {"id": "1", "type": "company"}
                },
                "other-organizations": {
                    "data": [
                        {"id": "2", "type": "company"},
                        {"id": "3", "type": "association"}
                    ]
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "company",
                "attributes": {
                    "name": "Company 1"
                },
            },
            {
                "id": "2",
                "type": "company",
                "attributes": {
                    "name": "Company 2"
                },
            },
            {
                "id": "3",
                "type": "association",
                "attributes": {
                    "name": "Association"
                },
            },
        ]
    }
