from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import force_text
from django.core.exceptions import ImproperlyConfigured
from rest_framework.compat import importlib
from rest_framework.serializers import ListSerializer, ManyRelatedField
from inflection import underscore, dasherize


def get_serializer(serializer):
    if isinstance(serializer, ListSerializer):
        return serializer.child
    if isinstance(serializer, ManyRelatedField):
        return serializer.child_relation
    return serializer


def get_model(related_field, field_name, serializer):
    queryset = getattr(related_field, "queryset", None)
    if queryset is not None:
        return queryset.model
    model = getattr(serializer.Meta, 'model_map', {}).get(field_name)
    if model:
        return model
    raise ImproperlyConfigured(
        "Related fields that do not have a queryset attribute "
        "(eg. read_only fields) must define the related model in the "
        "serializer's `model_map` attribute.")


def get_resource_type(model):
    RESOURCE_TYPE_EXTRACTOR = getattr(
        settings, "REST_FRAMEWORK", None).get("RESOURCE_TYPE_EXTRACTOR", None)
    if RESOURCE_TYPE_EXTRACTOR:
        try:
            parts = RESOURCE_TYPE_EXTRACTOR.split(".")
            module_path, class_name = ".".join(parts[:-1]), parts[-1]
            module = importlib.import_module(module_path)
            return getattr(module, class_name)(model)
        except (ImportError, AttributeError) as e:
            msg = ("Could not import '{}' for API setting "
                   "'RESOURCE_TYPE_EXTRACTOR'. {}: {}.".format(
                       RESOURCE_TYPE_EXTRACTOR, e.__class__.__name__, e))
            raise ImportError(msg)
    return force_text(dasherize(underscore(model._meta.object_name)).strip())
