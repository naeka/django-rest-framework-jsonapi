from __future__ import unicode_literals

from django.utils import six
from rest_framework.parsers import JSONParser
from rest_framework.serializers import BaseSerializer
from rest_framework.relations import RelatedField
from inflection import underscore, dasherize

from .utils import get_serializer


class JsonApiParser(JSONParser):
    media_type = "application/vnd.api+json"

    def parse(self, stream, media_type=None, parser_context=None):
        """Convert JSONAPI data to JSON data"""
        content = super(JsonApiParser, self).parse(
            stream, media_type=media_type, parser_context=parser_context)

        self.view = parser_context.get("view", None)

        if "data" in content:
            serializer = self.view.get_serializer(instance=None)
            fields = serializer.get_fields()

            resource_data = {}
            for attr_name, val in six.iteritems(
                    content["data"].pop("attributes", {})):
                resource_data[underscore(attr_name)] = val
            relationships = content["data"].pop("relationships", {})
            if content["data"].get("id"):
                resource_data.update(id=content["data"].pop("id"))

            for field_name, field in six.iteritems(fields):
                if dasherize(field_name) not in relationships:
                    continue

                related_field = get_serializer(field)

                if isinstance(related_field, (RelatedField, BaseSerializer)):
                    rel_data = relationships[dasherize(field_name)].get("data")
                    if rel_data:
                        if isinstance(rel_data, list):
                            rel_data = [data.get("id") for data in rel_data]
                        else:
                            rel_data = rel_data.get("id")
                    resource_data[underscore(field_name)] = rel_data
            return resource_data
        return {}
