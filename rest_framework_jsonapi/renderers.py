from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import force_text

from rest_framework.renderers import JSONRenderer
from rest_framework.relations import RelatedField, ManyRelatedField
from rest_framework.compat import OrderedDict
from inflection import dasherize
import re

from .utils import get_serializer, get_model, get_resource_type


class JsonApiRenderer(JSONRenderer):
    media_type = "application/vnd.api+json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Convert serialized response data to JSONAPI"""
        self.view = renderer_context.get("view", None)
        self.request = renderer_context.get("request", None)
        if self.view and hasattr(self.view, 'action') and \
           self.view.action == 'list':
            if isinstance(data, (dict, OrderedDict)) and "data" in data:
                self.hash = data
                self.hash["data"] = JsonApiAdapter(
                    self, data["data"]).serializable_hash()
            else:
                self.hash = JsonApiAdapter(self, data).serializable_hash()
        else:
            if hasattr(data, "serializer"):
                self.hash = JsonApiAdapter(self, data).serializable_hash()
            else:
                # Errors
                self.hash = {"errors": data}

        return super(JsonApiRenderer, self).render(
            data=self.hash, accepted_media_type=accepted_media_type,
            renderer_context=renderer_context)


class JsonApiAdapter(object):
    def __init__(self, renderer, serialized_data, serializer=None):
        self.renderer = renderer
        self.serialized_data = serialized_data
        if serializer:
            self.serializer = get_serializer(serializer)
        else:
            self.serializer = get_serializer(serialized_data.serializer)
        self.hash = OrderedDict({"data": []})
        self.included_set = set()

    def serializable_hash(self):
        if isinstance(self.serialized_data, list):
            for obj in self.serialized_data:
                result = JsonApiAdapter(self.renderer, obj,
                                        self.serializer).serializable_hash()
                self.hash["data"].append(result.get("data"))
                if result.get("included"):
                    if "included" not in self.hash:
                        self.hash["included"] = []
                    for result in result.get("included"):
                        set_key = "-".join([result.get("type"),
                                            result.get("id")])
                        if set_key not in self.included_set:
                            self.hash["included"].append(result)
                            self.included_set.add(set_key)
        else:
            self.hash["data"] = self.attributes_for_serialized_data(
                self.serialized_data, self.serializer)
            self.add_resource_relationships(
                self.hash["data"], self.serialized_data, self.serializer)
        return self.hash

    def add_relationships(self, resource, rel_name, relationship):
        dash_name = dasherize(rel_name)
        if dash_name not in resource["relationships"]:
            resource["relationships"][dash_name] = OrderedDict({
                "data": []
            })
        if relationship.get("data"):
            for data in relationship.get("data"):
                try:
                    rel_id = data.get("id")  # Serialized data
                except AttributeError:
                    rel_id = data  # Only IDs
                resource["relationships"][dash_name]["data"].append(
                    OrderedDict([
                        ("id", force_text(rel_id)),
                        ("type", relationship.get("type")),
                    ])
                )

    def add_relationship(self, resource, rel_name, relationship):
        dash_name = dasherize(rel_name)
        if dash_name not in resource["relationships"]:
            resource["relationships"][dash_name] = OrderedDict({
                "data": None
            })
        if relationship.get("data"):
            try:
                rel_id = relationship.get("data").get("id")  # Serialized data
            except AttributeError:
                rel_id = relationship.get("data")  # Only ID
            resource["relationships"][dasherize(rel_name)]["data"] = \
                OrderedDict([
                    ("id", force_text(rel_id)),
                    ("type", relationship.get("type")),
                ])

    def add_included(self, rel_name, relationship, parent=None):
        included_serializer = self.get_included_serializer(
            relationship.get("parent_serializer"), rel_name)
        if not included_serializer:
            return
        serialized_data = relationship.get("data")
        if not isinstance(serialized_data, list):
            serialized_data = [serialized_data]
        included_data = []
        for item in serialized_data:
            if isinstance(item, int):
                # Only ID
                data = self.get_included_data(
                    rel_name, item, included_serializer)
                if data:
                    included_data.append(data)

        resource_path = ".".join([parent, rel_name] if parent else [rel_name])
        if self.include_assoc(resource_path):
            if "included" not in self.hash:
                self.hash["included"] = []
            for data in included_data:
                attrs = self.attributes_for_serialized_data(
                    data, included_serializer)
                self.add_resource_relationships(
                    attrs, data, included_serializer, add_included=False)
                if attrs not in self.hash.get("included"):
                    self.hash["included"].append(attrs)

        if self.include_nested_assoc(resource_path):
            for data in included_data:
                relationships = self.get_relationships_data(
                    data, included_serializer)
                for rel_name, relationship in six.iteritems(relationships):
                    self.add_included(rel_name, relationship)

    def get_included_serializer(self, serializer, rel_name):
        return getattr(serializer.Meta, "include", {}).get(rel_name)

    def get_included_data(self, rel_name, pk, included_serializer):
        model = included_serializer.Meta.model
        obj = model.objects.get(pk=pk)
        return included_serializer.to_representation(obj)

    def attributes_for_serialized_data(self, serialized_data, serializer):
        if isinstance(serialized_data, list):
            result = []
            for obj in serialized_data:
                result.append(self.resource_object_for(obj, serializer))
        else:
            result = self.resource_object_for(serialized_data, serializer)
        return result

    def resource_object_for(self, obj, serializer):
        attributes = self.get_attributes_data(obj, serializer)
        result = OrderedDict([
            ("id", force_text(attributes.pop("id"))),
            ("type", attributes.pop("type")),
        ])
        if attributes:
            result["attributes"] = attributes
        return result

    def add_resource_relationships(self, attrs, serialized_data, serializer,
                                   add_included=True):
        relationships = self.get_relationships_data(serialized_data,
                                                    serializer)
        if relationships and "relationships" not in attrs:
            attrs["relationships"] = OrderedDict()
        for rel_name, relationship in six.iteritems(relationships):
            if isinstance(relationship.get("data"), list):
                self.add_relationships(attrs, rel_name, relationship)
            else:
                self.add_relationship(attrs, rel_name, relationship)
            if add_included:
                self.add_included(rel_name, relationship)

    def include_assoc(self, assoc):
        return self.check_assoc("{}$".format(assoc))

    def include_nested_assoc(self, assoc):
        return self.check_assoc("{}.".format(assoc))

    def check_assoc(self, assoc):
        include_opt = self.renderer.request.QUERY_PARAMS.get("include")
        if not include_opt:
            return False
        include_opt = include_opt.split(",")
        for opt in include_opt:
            if re.match(r"^{}".format(assoc.replace(".", "\.")), opt):
                return True
        return False

    def get_attributes_data(self, obj, serializer):
        model = serializer.Meta.model
        resource_type = get_resource_type(model)
        attributes = OrderedDict([("id", None), ("type", resource_type)])

        for field_name, field in six.iteritems(serializer.get_fields()):
            if isinstance(field, (RelatedField, ManyRelatedField)):
                continue
            attributes[dasherize(field_name)] = obj.get(field_name)
        return attributes

    def get_relationships_data(self, serialized_data, serializer):
        relationships = OrderedDict()
        for field_name, field in serializer.get_fields().items():
            if isinstance(field, (RelatedField, ManyRelatedField)):
                relationships[field_name] = {
                    "field": field,
                    "parent_serializer": serializer,
                    "data": serialized_data.get(field_name)
                }
                related_field = get_serializer(field)
                relationships[field_name]["type"] = get_resource_type(
                    get_model(related_field))
        return relationships
