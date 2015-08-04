# Usage

---


!!! note "JSONAPI specification is more than just a serialization format"

    Even if we're only using DRF renderers here, JSONAPI resources must be designed consequently: complex resources with nested
    serializers or containing any other related field than `PrimaryKeyRelatedField` are not supported since they would excessively
    mess the rendering process.

    That way, if you need to expose both conventional API and JSONAPI, please do not rely on DRF's content negociation and implement
    different API aside, according to your needs. Your stack will be much simpler.

## Renderer and parser classes

Depending on how important are JSONAPI resources for your DRF project, you would either define as the default renderer/parser in your DRF settings:

```python
REST_FRAMEWORK={
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_jsonapi.renderers.JsonApiRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_jsonapi.parsers.JsonApiParser",
    ),
}
```

Or define them on your views:

```python
from rest_framework_jsonapi.renderers import JsonApiRenderer
from rest_framework_jsonapi.parsers import JsonApiParser


# On your class based views:

class ExampleView(APIView):
    renderer_classes = (JsonApiRenderer,)
    parser_classes = (JsonApiParser,)

    def post(self, request, format=None):
        # Your code


# Or on your function based views, using this decorator:

@api_view(["GET", "POST"])
@renderer_classes((JsonApiRenderer,))
@parser_classes((JsonApiParser,))
def example_view(request, format=None):
    # Your code
```

## Pagination


### Settings

Likewise, pagination can be set as the default in the settings:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework_jsonapi.pagination.CursorPagination"
}
```

Or directly defined on a view:

```python
from rest_framework_jsonapi.pagination import LimitOffsetPagination


class PaginatedView(generics.ListAPIView):
    pagination_class = LimitOffsetPagination
```


The DRF default pagination classes are extended to be compliant with JSONAPI.
However, because of their internals, they do not expose pagination info the same way.

### PageNumberPagination

    rest_framework_jsonapi.pagination.PageNumberPagination

This pagination system accepts the following parameters:

- `page[number]`

And provides:

- The 4 links objects (`first`/`last`/`prev`/`next`)
- The total number of objects as `count` in the `meta` object

By default, the size is determined by the server and set in DRF settings (the `PAGE_SIZE` settings) or at the view level.
However, it can be inherited to support a size query parameter by defining its `page_size_query_param` like this:

```python
class SizedPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page[size]"
```

The returned payload looks like this:

```json
{
    "links": {
        "first": "http://testserver/people",
        "last": "http://testserver/people?page%5Bnumber%5D=2",
        "prev": null,
        "next": "http://testserver/people?page%5Bnumber%5D=2"
    },
    "meta": {
        "count": 4
    },
    "data": {
        "data": [
            /* ... */
        ]
    }
}
```

!!! note "Note:"
    As you can notice, query params are percent-encoded.
    This could seems odd but this is the expected JSONAPI behaviour, as stated here:

        Note: The above example URI shows unencoded [ and ] characters simply for readability.
        In practice, these characters must be percent-encoded, per the requirements in RFC 3986.

    -- [JSONAPI specification](http://jsonapi.org/format/#fetching-sparse-fieldsets) /
    [RFC 3986](http://tools.ietf.org/html/rfc3986#section-3.4)


### LimitOffsetPagination

    rest_framework_jsonapi.pagination.LimitOffsetPagination

This pagination system accepts the following parameters:

- `page[limit]`
- `page[offset]`

And provides:

- 2 links objects (`prev` and `next`)
- The total number of objects as `count` in the `meta` object

The returned payload looks like this:

```json
{
    "links": {
        "prev": null,
        "next": "http://testserver/people?page%5Boffset%5D=3"
    },
    "meta": {
        "count": 4
    },
    "data": {
        "data": [
            /* ... */
        ]
    }
}
```

### CursorPagination

    rest_framework_jsonapi.pagination.CursorPagination

This pagination system accepts the following parameters:

- `page[cursor]`

And provides:

- 2 links objects (`prev` and `next`)

Cursor pagination is ordered. By default the ordering is `id` (ascending).
It can be inherited to to order on a descending datetime field for example:

```python
class DatetimeCursorPagination(CursorPagination):
    ordering = "-created_at"
```

The returned payload looks like this:

```json
{
    "links": {
        "prev": None,
        "next": "http://testserver/people?page%5Bcursor%5D=cD0z"
    },
    "data": {
        "data": [
            /* ... */
        ]
    }
}
```


## Error handling

JSONAPI requires a specific format for error responses.
Field errors must point to a specific field according to a materialized path (e.g. `/data/attributes/last-name`).

The `EXCEPTION_HANDLER` must be defined on your `REST_FRAMEWORK` settings:
```python
REST_FRAMEWORK={
    "EXCEPTION_HANDLER":
        "rest_framework_jsonapi.views.exception_handler",
}
```

!!! warning "Warning:"
    Exceptions that does not inherit from `APIException`, `Http404` or `PermissionDenied` does not
    generate responses but `HTTP 500` errors.


## Sideloading

JSONAPI is a flat format. Thus, relations can't be nested.

If you want to query `users`, you'll get zero, one or more users with their attributes and relationships described.
To retrieve user's `groups` or `profile` relationships, you can fetch them from their own endpoints.

Unfortunately, in some cases, this led to numerous queries. To avoid this, you can use sideloading.

Sideloadling provides a distinct flat list of a specific payload related data.

Django Rest Framework JSONAPI allows the configuration of included relationships per serializer.
There's no registry-like system which can automate this process because sideloading is not suitable in each case.

This is configured like this:

```python
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff", "groups")
        include = {
            "groups": GroupSerializer(),
        }


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name", "creator")
        include = {
            "creator": UserSerializer(),
        }
```

Starting from that, a request like this one:
```http
GET /api/users/1
```

Would return a payload like that:

```json
{
    "data": {
        "id": "1",
        "type": "users",
        "attributes": {
            "username": "user1",
            "email": "user1@example.com",
            "is_staff": true
        },
        "relationships": {
            "groups": {
                "data": [
                    {"id": "1", "type": "groups"}
                ]
            }
        }
    }
}
```

A request like this one:
```http
GET /api/users/1?include=groups
```

Would return a payload like that, with the related group sideloaded:

```
{
    "data": {
        "id": "1",
        "type": "users",
        "attributes": {
            "username": "user1",
            "email": "user1@example.com",
            "is_staff": true
        },
        "relationships": {
            "groups": {
                "data": [
                    {"id": "1", "type": "groups"}
                ]
            }
        }
    },
    "included": [
        {
            "id": "1",
            "type": "groups",
            "attributes": {
                "name": "group1"
            },
            "relationships": {
                "creator": {
                    "data": {"id": "2", "type": "users"}
                }
            }
        }
    ]
}
```

And a request like this one:
```http
GET /api/users/1?include=groups,groups.creator
```

Would return a payload like that, with the related group and creator sideloaded:

```
{
    "data": {
        "id": "1",
        "type": "users",
        "attributes": {
            "username": "user1",
            "email": "user1@example.com",
            "is_staff": true
        },
        "relationships": {
            "groups": {
                "data": [
                    {"id": "1", "type": "groups"}
                ]
            }
        }
    },
    "included": [
        {
            "id": "1",
            "type": "groups",
            "attributes": {
                "name": "group1"
            },
            "relationships": {
                "creator": {
                    "data": {"id": "2", "type": "users"}
                }
            }
        },
        {
            "id": "2",
            "type": "users",
            "attributes": {
                "username": "user2",
                "email": "user2@example.com",
                "is_staff": false
            },
            "relationships": {
                "groups": {
                    "data": [
                        {"id": "1", "type": "groups"}
                    ]
                }
            }
        }
    ]
}
```

!!! note "Note:"
    The `included` list is distinct. When building it only appends objects that aren't currently in.
    Facing the nested paradigm, this is truly effective and bandwidth savvy when rendering lists with many related data.