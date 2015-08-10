drf-jsonapi
======================================

|build-status-image| |pypi-version| |read-the-docs|

Overview
--------

Django Rest Framework tools which are compliant with the JSONAPI 1.0 specification.

Documentation: `django-rest-framework-jsonapi.rtfd.org`_

Requirements
------------

-  Python (2.7, 3.4)
-  Django (1.6, 1.7, 1.8)
-  Django REST Framework (3.1)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install drf-jsonapi

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ ./runtests.py

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

Documentation
-------------

The documentation is browsable on Read the Docs: `django-rest-framework-jsonapi.rtfd.org`_

To build the documentation, you’ll need to install ``mkdocs``.

.. code:: bash

    $ pip install mkdocs

To preview the documentation:

.. code:: bash

    $ mkdocs serve
    Running at: http://127.0.0.1:8000/

To build the documentation:

.. code:: bash

    $ mkdocs build

.. _tox: http://tox.readthedocs.org/en/latest/
.. _django-rest-framework-jsonapi.rtfd.org: http://django-rest-framework-jsonapi.rtfd.org/

.. |build-status-image| image:: https://secure.travis-ci.org/Naeka/django-rest-framework-jsonapi.svg?branch=master
   :target: http://travis-ci.org/Naeka/django-rest-framework-jsonapi?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/drf-jsonapi.svg
   :target: https://pypi.python.org/pypi/drf-jsonapi
.. |read-the-docs| image:: https://readthedocs.org/projects/django-rest-framework-jsonapi/badge/?version=stable
   :target: http://django-rest-framework-jsonapi.rtfd.org
