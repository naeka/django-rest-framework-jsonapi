from django.utils.encoding import force_text
from rest_framework.serializers import ListSerializer, ManyRelatedField


def get_serializer(serializer):
    if isinstance(serializer, ListSerializer):
        return serializer.child
    if isinstance(serializer, ManyRelatedField):
        return serializer.child_relation
    return serializer


def get_model(obj):
    model = getattr(obj, "model", None)
    if model:
        return model
    queryset = getattr(obj, "queryset", None)
    if queryset is not None:
        return queryset.model


def get_resource_type(model):
    return force_text(model._meta.verbose_name_plural).replace(" ", "-")
