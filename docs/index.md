<div class="badges">
    <a href="http://travis-ci.org/Naeka/django-rest-framework-jsonapi">
        <img src="https://travis-ci.org/Naeka/django-rest-framework-jsonapi.svg?branch=master">
    </a>
    <a href="https://pypi.python.org/pypi/drf-jsonapi">
        <img src="https://img.shields.io/pypi/v/drf-jsonapi.svg">
    </a>
    <a href='http://django-rest-framework-jsonapi.rtfd.org'>
        <img src='https://readthedocs.org/projects/django-rest-framework-jsonapi/badge/?version=stable' />
    </a>
</div>

---

# Django Rest Framework JSONAPI

---

## Overview

Django Rest Framework tools which are compliant with the JSONAPI 1.0 specification

Documentation: [django-rest-framework-jsonapi.rtfd.org](http://django-rest-framework-jsonapi.rtfd.org)

## Requirements

* Python (2.7, 3.4)
* Django (1.6, 1.7, 1.8)
* Django Rest Framework 3.1

## Installation

Install using `pip`

```bash
$ pip install drf-jsonapi
```

## Example

Let's take a look at a quick example of using Django Rest Framework JSONAPI to build a simple model-backed API, served as JSONAPI.

We'll create a read-write API for accessing information on the users of our project.

Any global settings for a REST framework API are kept in a single configuration dictionary named `REST_FRAMEWORK`.
Start off by adding the following to your `settings.py` module:

```python
REST_FRAMEWORK={
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_jsonapi.renderers.JsonApiRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_jsonapi.parsers.JsonApiParser",
    ),
    "EXCEPTION_HANDLER": "rest_framework_jsonapi.views.exception_handler",
}
```

Don't forget to make sure you've also added `rest_framework` to your `INSTALLED_APPS`.

We're ready to create our API now. Here's our project's root `urls.py` module:

```python
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "url", "username", "email", "is_staff")

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework"))
]
```

You can now open the API in your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/), and view your new 'users' API.
If you use the login control in the top right corner you'll also be able to add, create and delete users from the system.
