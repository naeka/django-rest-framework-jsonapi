from collections import OrderedDict
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from .utils import get_resource_type


class JsonApiPrimaryKeyRelatedField(PrimaryKeyRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, obj):
        ret = OrderedDict([
            ('id', obj.pk),
            ('_drf_jsonapi_type', get_resource_type(obj._meta.model)),
        ])
        ret._is_related = True
        return ret


class JsonApiSerializerMixin(object):
    serializer_related_field = JsonApiPrimaryKeyRelatedField

    def to_representation(self, instance):
        ret = super(JsonApiSerializerMixin, self).to_representation(instance)
        ret['_drf_jsonapi_type'] = get_resource_type(instance._meta.model)
        return ret


class JsonApiSerializer(JsonApiSerializerMixin, serializers.ModelSerializer):
    pass
