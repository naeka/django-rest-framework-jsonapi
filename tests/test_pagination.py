from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import json
import pytest

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
                "type": "articles",
                "attributes": {
                    "title": "Molly's article"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "1",
                            "type": "persons"
                        }
                    },
                    "comments": {
                        "data": []
                    }
                }
            },
            {
                "id": "2",
                "type": "articles",
                "attributes": {
                    "title": "Buzz' article"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "2",
                            "type": "persons"
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
                    "type": "articles",
                    "attributes": {
                        "title": "Molly's article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "1",
                                "type": "persons"
                            }
                        },
                        "comments": {
                            "data": []
                        }
                    }
                },
                {
                    "id": "2",
                    "type": "articles",
                    "attributes": {
                        "title": "Buzz' article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "2",
                                "type": "persons"
                            }
                        },
                        "comments": {
                            "data": []
                        }
                    }
                },
                {
                    "id": "3",
                    "type": "articles",
                    "attributes": {
                        "title": "Sid's article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "3",
                                "type": "persons"
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
                    "type": "articles",
                    "attributes": {
                        "title": "Bo's article"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "4",
                                "type": "persons"
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
    assert json.loads(response.content.decode()) == {
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
                    "type": "persons",
                    "attributes": {
                        "first-name": "Molly",
                        "last-name": "Davis",
                        "twitter": ""
                    }
                },
                {
                    "id": "2",
                    "type": "persons",
                    "attributes": {
                        "first-name": "Buzz",
                        "last-name": "Lightyear",
                        "twitter": ""
                    }
                },
                {
                    "id": "3",
                    "type": "persons",
                    "attributes": {
                        "first-name": "Sid",
                        "last-name": "Phillips",
                        "twitter": ""
                    }
                }
            ]
        }
    }

    next_response = client.get("http://testserver/people?page%5Boffset%5D=3")
    assert json.loads(next_response.content.decode()) == {
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
                    "type": "persons",
                    "attributes": {
                        "first-name": "Bo",
                        "last-name": "Peep",
                        "twitter": ""
                    }
                }
            ]
        }
    }


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
                    "type": "comments",
                    "attributes": {
                        "body": "Molly's comment"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "1",
                                "type": "persons"
                            }
                        }
                    }
                },
                {
                    "id": "2",
                    "type": "comments",
                    "attributes": {
                        "body": "Buzz' comment"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "2",
                                "type": "persons"
                            }
                        }
                    }
                },
                {
                    "id": "3",
                    "type": "comments",
                    "attributes": {
                        "body": "Sid's comment"
                    },
                    "relationships": {
                        "author": {
                            "data": {
                                "id": "3",
                                "type": "persons"
                            }
                        }
                    }
                }
            ],
            "included": [
                {
                    "id": "1",
                    "type": "persons",
                    "attributes": {
                        "first-name": "Molly",
                        "last-name": "Davis",
                        "twitter": ""
                    }
                },
                {
                    "id": "2",
                    "type": "persons",
                    "attributes": {
                        "first-name": "Buzz",
                        "last-name": "Lightyear",
                        "twitter": ""
                    }
                },
                {
                    "id": "3",
                    "type": "persons",
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
                "type": "comments",
                "attributes": {
                    "body": "Bo's comment"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "id": "4",
                            "type": "persons"
                        }
                    }
                }
            }
        ],
        "included": [
            {
                "id": "4",
                "type": "persons",
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
