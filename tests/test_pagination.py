from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest
import rest_framework

from tests.models import Article, Person, Comment


pytestmark = pytest.mark.django_db


def test_no_pagination_if_all_results(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    Article.objects.create(title="Molly's article", author=molly)
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Article.objects.create(title="Buzz' article", author=buzz)
    response = client.get(reverse("article-list"))
    assert json.loads(response.content.decode()) == {
        "data": [
            {
                "id": "1",
                "type": "article",
                "attributes": {
                    "title": "Molly's article"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "1",
                            "type": "person"
                        }
                    },
                    "comments": {
                        "data": []
                    }
                }
            },
            {
                "id": "2",
                "type": "article",
                "attributes": {
                    "title": "Buzz' article"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "2",
                            "type": "person"
                        }
                    },
                    "comments": {
                        "data": []
                    }
                }
            }
        ]
    }


def test_page_number(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    Article.objects.create(title="Molly's article", author=molly)
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Article.objects.create(title="Buzz' article", author=buzz)
    sid = Person.objects.create(last_name="Phillips", first_name="Sid")
    Article.objects.create(title="Sid's article", author=sid)
    bo = Person.objects.create(last_name="Peep", first_name="Bo")
    Article.objects.create(title="Bo's article", author=bo)
    response = client.get(reverse("article-list"))
    assert json.loads(response.content.decode()) == {
        "links": {
            "first": "http://testserver/articles",
            "last": "http://testserver/articles?page%5Bnumber%5D=2",
            "prev": None,
            "next": "http://testserver/articles?page%5Bnumber%5D=2"
        },
        "meta": {
            "count": 4
        },
        "data": {
            "data": [
                {
                    "id": "1",
                    "type": "article",
                    "attributes": {
                        "title": "Molly's article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "1",
                                "type": "person"
                            }
                        },
                        "comments": {
                            "data": []
                        }
                    }
                },
                {
                    "id": "2",
                    "type": "article",
                    "attributes": {
                        "title": "Buzz' article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "2",
                                "type": "person"
                            }
                        },
                        "comments": {
                            "data": []
                        }
                    }
                },
                {
                    "id": "3",
                    "type": "article",
                    "attributes": {
                        "title": "Sid's article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "3",
                                "type": "person"
                            }
                        },
                        "comments": {
                            "data": []
                        }
                    }
                }
            ]
        }
    }

    next_response = client.get("http://testserver/articles?page%5Bnumber%5D=2")
    assert json.loads(next_response.content.decode()) == {
        "links": {
            "first": "http://testserver/articles",
            "last": "http://testserver/articles?page%5Bnumber%5D=2",
            "prev": "http://testserver/articles",
            "next": None
        },
        "meta": {
            "count": 4
        },
        "data": {
            "data": [
                {
                    "id": "4",
                    "type": "article",
                    "attributes": {
                        "title": "Bo's article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "4",
                                "type": "person"
                            }
                        },
                        "comments": {
                            "data": []
                        }
                    }
                }
            ]
        }
    }


def test_limit_offset(client):
    Person.objects.create(last_name="Davis", first_name="Molly")
    Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Person.objects.create(last_name="Phillips", first_name="Sid")
    Person.objects.create(last_name="Peep", first_name="Bo")
    response = client.get(reverse("person-list"))
    expected = {
        "links": {
            "prev": None,
            "next": "http://testserver/people?page%5Boffset%5D=3"
        },
        "meta": {
            "count": 4
        },
        "data": {
            "data": [
                {
                    "id": "1",
                    "type": "person",
                    "attributes": {
                        "first-name": "Molly",
                        "last-name": "Davis",
                        "twitter": ""
                    }
                },
                {
                    "id": "2",
                    "type": "person",
                    "attributes": {
                        "first-name": "Buzz",
                        "last-name": "Lightyear",
                        "twitter": ""
                    }
                },
                {
                    "id": "3",
                    "type": "person",
                    "attributes": {
                        "first-name": "Sid",
                        "last-name": "Phillips",
                        "twitter": ""
                    }
                }
            ]
        }
    }
    # Limit is always included since DRF 3.2 (35c28a2)
    if rest_framework.__version__.split(".")[1] >= "2":
        expected["links"]["next"] = "http://testserver/people?page%5Blimit%5D"\
                                    "=3&page%5Boffset%5D=3"
    assert json.loads(response.content.decode()) == expected

    next_response = client.get("http://testserver/people?page%5Boffset%5D=3")
    expected = {
        "links": {
            "prev": "http://testserver/people",
            "next": None
        },
        "meta": {
            "count": 4
        },
        "data": {
            "data": [
                {
                    "id": "4",
                    "type": "person",
                    "attributes": {
                        "first-name": "Bo",
                        "last-name": "Peep",
                        "twitter": ""
                    }
                }
            ]
        }
    }
    # Limit is always included since DRF 3.2 (35c28a2)
    if rest_framework.__version__.split(".")[1] >= "2":
        expected["links"]["prev"] += "?page%5Blimit%5D=3"
    assert json.loads(next_response.content.decode()) == expected


def test_cursor_and_sideloading(client):
    molly = Person.objects.create(last_name="Davis", first_name="Molly")
    Comment.objects.create(body="Molly's comment", author=molly)
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    sid = Person.objects.create(last_name="Phillips", first_name="Sid")
    Comment.objects.create(body="Sid's comment", author=sid)
    bo = Person.objects.create(last_name="Peep", first_name="Bo")
    Comment.objects.create(body="Bo's comment", author=bo)
    response = client.get("{}?include=author".format(reverse("comment-list")))
    assert json.loads(response.content.decode()) == {
        "links": {
            "prev": None,
            "next": "http://testserver/comments?include=author"
                    "&page%5Bcursor%5D=cD0z"
        },
        "data": {
            "data": [
                {
                    "id": "1",
                    "type": "comment",
                    "attributes": {
                        "body": "Molly's comment"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "1",
                                "type": "person"
                            }
                        }
                    }
                },
                {
                    "id": "2",
                    "type": "comment",
                    "attributes": {
                        "body": "Buzz' comment"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "2",
                                "type": "person"
                            }
                        }
                    }
                },
                {
                    "id": "3",
                    "type": "comment",
                    "attributes": {
                        "body": "Sid's comment"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "3",
                                "type": "person"
                            }
                        }
                    }
                }
            ],
            "included": [
                {
                    "id": "1",
                    "type": "person",
                    "attributes": {
                        "first-name": "Molly",
                        "last-name": "Davis",
                        "twitter": ""
                    }
                },
                {
                    "id": "2",
                    "type": "person",
                    "attributes": {
                        "first-name": "Buzz",
                        "last-name": "Lightyear",
                        "twitter": ""
                    }
                },
                {
                    "id": "3",
                    "type": "person",
                    "attributes": {
                        "first-name": "Sid",
                        "last-name": "Phillips",
                        "twitter": ""
                    }
                }
            ]
        }
    }

    next_response = client.get("http://testserver/comments?include=author"
                               "&page%5Bcursor%5D=cD0z")
    response_data = json.loads(next_response.content.decode())
    assert response_data["data"] == {
        "data": [
            {
                "id": "4",
                "type": "comment",
                "attributes": {
                    "body": "Bo's comment"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "4",
                            "type": "person"
                        }
                    }
                }
            }
        ],
        "included": [
            {
                "id": "4",
                "type": "person",
                "attributes": {
                    "first-name": "Bo",
                    "last-name": "Peep",
                    "twitter": ""
                }
            }
        ]
    }
    assert response_data["links"]["prev"] in [
        "http://testserver/comments?include=author"
        "&page%5Bcursor%5D=cj0xJnA9NA%3D%3D",
        "http://testserver/comments?include=author"
        "&page%5Bcursor%5D=cD00JnI9MQ%3D%3D",
    ]
    assert response_data["links"]["next"] is None
