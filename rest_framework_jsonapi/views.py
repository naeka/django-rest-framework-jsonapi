from __future__ import unicode_literals

from django.utils import six
from rest_framework.views import exception_handler as drf_exception_handler
from inflection import dasherize


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        # Unhandled exceptions will raise a 500 error.
        return

    errors = []
    # Handle views errors
    if isinstance(response.data, list):
        for message in response.data:
            errors.append({
                "detail": message,
                "source": {
                    "pointer": "/data",
                },
                "status": six.text_type(response.status_code),
            })
    # Handle all other errors
    elif isinstance(response.data, dict):
        for field, error in response.data.items():
            # Field errors
            if isinstance(error, list):
                field = dasherize(field)
                pointer = "/data/attributes/{}".format(field)
                for message in error:
                    errors.append({
                        "detail": message,
                        "source": {
                            "pointer": pointer,
                        },
                        "status": six.text_type(response.status_code),
                    })
            # Other errors (e.g. Http404, PermissionDenied, throttling errors)
            elif field == "detail" and isinstance(error, six.string_types):
                errors.append({
                    "detail": error,
                    "source": {
                        "pointer": "/data",
                    },
                    "status": six.text_type(response.status_code),
                })

    response.data = errors
    return response
