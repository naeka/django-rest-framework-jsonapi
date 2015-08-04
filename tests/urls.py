from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework import routers

from tests.views import (
    Articles, People, Comments, OnlyComments, throttled_view,
    validation_error_view, errored_view
)


router = routers.DefaultRouter(trailing_slash=False)

router.register(r"articles", Articles)
router.register(r"people", People)
router.register(r"comments", Comments)
router.register(r"only-comments", OnlyComments, base_name="only-comment")

urlpatterns = router.urls + [
    url(r"^throttled-view$", throttled_view, name="throttled-view"),
    url(r"^validation-error-view$", validation_error_view,
        name="validation-error-view"),
    url(r"^errored-view$", errored_view, name="errored-view"),
]
