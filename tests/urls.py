from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework import routers

from tests.views import (
    Articles, People, AuthenticatedPeople, Comments, OnlyComments,
    ImproperlyConfiguredReadOnlyAuthorComments, ReadOnlyAuthorComments,
    FormattingWithABBRs, throttled_view, validation_error_view,
    errored_view
)


router = routers.DefaultRouter(trailing_slash=False)

router.register(r"articles", Articles)
router.register(r"people", People)
router.register(r"auth-people", AuthenticatedPeople, base_name="auth-people")
router.register(r"comments", Comments)
router.register(r"only-comments", OnlyComments, base_name="only-comment")
router.register(r"ic-read-only-author-comments",
                ImproperlyConfiguredReadOnlyAuthorComments,
                base_name="ic-read-only-author-comment")
router.register(r"read-only-author-comments", ReadOnlyAuthorComments,
                base_name="read-only-author-comment")
router.register(r"formatting", FormattingWithABBRs,
                base_name="formatting")

urlpatterns = router.urls + [
    url(r"^throttled-view$", throttled_view, name="throttled-view"),
    url(r"^validation-error-view$", validation_error_view,
        name="validation-error-view"),
    url(r"^errored-view$", errored_view, name="errored-view"),
]
