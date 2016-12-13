"""Manage relationships between resources."""

from __future__ import unicode_literals
from inflection import pluralize
from . import (
    CB,
    Resource,
    build_request_relationship,
    build_request_include
)


class RelationType(object):
    """Defines the way a relationship is fetched.

    The Helium API does not require an include directive to also mean
    a full URL relationship. This means that for some relationships
    you use the URL where for others you use an ``include`` paramater
    to get the related objects.

    For example::

        https://api.helium.com/v1/label/<id>/sensor
        https://api.helium.com/v1/label/<id>?include=sensor

    The constants in this class define how the relationship functions
    should be looked up.
    """

    INCLUDE = b"include"
    """Use the include parameter relationship approach"""

    DIRECT = b"direct"
    """Use the direct relationship approach"""


def _build_relatonship(self, dest_resource_type, objs):
    session = self._session
    id = None if self.is_singleton() else self.id
    url = session._build_url(self._resource_path(), id,
                             'relationships', dest_resource_type)
    if objs is None:
        json = build_request_relationship(dest_resource_type, objs)
    elif isinstance(objs, Resource):
        json = build_request_relationship(dest_resource_type, objs.id)
    else:
        json = build_request_relationship(dest_resource_type,
                                          [obj.id for obj in objs])
    return (session, url, json)


def to_one(dest_class, type=RelationType.DIRECT, resource_classes=None,
           reverse=None, reverse_type=RelationType.DIRECT,
           writable=False):
    """Create a one to one relation to a given target :class:`Resource`.

    Args:

        dest_class(Resource): The *target* class for the relationship

    Keyword Args:

        type(RelationType): The relationship approach to use.
        reverse(to_may or to_one): An *optional* reverse relationship.
        reverse_type(RelationType): The reverse relationship approach.
        resource_classes(Resource): The kinds of Resources to expect
            in the relationship

    Returns:

        A builder function which, given a source class creates a
        one-to-one relationship with the target

    A one to one relationship means that you can get the associated
    target object from the object on which the ``to_one`` was declared.

    .. code-block:: python

        @to_one(Organization)
        def User(Resource):
            pass

    Declares that a User is associated with *one* Organization. The
    decorator automatically adds a method to fetch the associated
    organization:

    .. code-block:: python

        org = user.organization()

    """
    def method_builder(cls):
        dest_resource_type = dest_class._resource_type()
        dest_method_name = dest_resource_type.replace('-', '_')
        doc_variables = {
            'from_class': cls.__name__,
            'to_class': dest_class.__name__,
            'to_name': dest_method_name
        }

        fetch_method_doc = """Fetch the {2} associated with this :class:`{0}`.

        Returns:

          {1}: The :class:`{1}` of this :class:`{0}`
        """.format(cls.__name__, dest_class.__name__, dest_method_name)

        def _fetch_relationship_included(self):
            session = self._session
            include = self._include
            if include is None or dest_class not in include:
                # You requested an included relationship that was
                # not originally included
                error = "{} was not included".format(dest_class.__name__)
                raise AttributeError(error)
            included = self._included.get(dest_resource_type)
            if len(included) == 0:
                return None
            mk_one = dest_class._mk_one(session,
                                        resource_classes=resource_classes)
            return mk_one({
                'data': included[0]
            })

        def fetch_relationship_direct(self, use_included=False):
            if use_included:
                return _fetch_relationship_included(self)
            session = self._session
            id = None if self.is_singleton() else self.id
            url = session._build_url(self._resource_path(), id,
                                     dest_resource_type)
            process = dest_class._mk_one(session,
                                         resource_classes=resource_classes)
            return session.get(url, CB.json(200, process))

        def fetch_relationship_include(self, use_included=False):
            if use_included:
                return _fetch_relationship_included(self)
            session = self._session
            id = None if self.is_singleton() else self.id
            url = session._build_url(self._resource_path(), id)
            params = build_request_include([dest_class], None)

            def _process(json):
                included = json.get('included')
                if len(included) == 0:
                    return None

                mk_one = dest_class._mk_one(session,
                                            resource_classes=resource_classes)
                return mk_one({
                    'data': included[0]
                })
            return session.get(url, CB.json(200, _process),
                               params=params)

        if type == RelationType.DIRECT:
            fetch_relationship = fetch_relationship_direct
        elif type == RelationType.INCLUDE:
            fetch_relationship = fetch_relationship_include
        else:  # pragma: no cover
            raise ValueError("Invalid RelationType: {}".format(type))

        fetch_relationship.__doc__ = fetch_method_doc

        def update_method(self, resource):
            """Set the {to_name} for this :class:`{from_class}`.

            Args:

              resource: The :class:`{to_class}` to set

            Returns:

                True if successful
            """
            session, url, json = _build_relatonship(self, dest_resource_type,
                                                    resource)
            return session.patch(url, CB.boolean(200), json=json)

        methods = [(dest_method_name, fetch_relationship)]
        if writable:
            methods.extend([
                ('update_{}'.format(dest_method_name), update_method)
            ])
        for name, method in methods:
            method.__doc__ = method.__doc__.format(**doc_variables)
            setattr(cls, name, method)

        if reverse is not None:
            reverse(cls, type=reverse_type)(dest_class)

        return cls

    return method_builder


def to_many(dest_class, type=RelationType.DIRECT,
            reverse=None, reverse_type=RelationType.DIRECT,
            resource_classes=None, writable=False):
    """Create a one to many relation to a given target :class:`Resource`.

    Args:

        dest_class(Resource): The *target* class for the relationship

    Keyword Args:

        type(RelationType): The relationship approach to use.
        writable(bool): Whether the relationship is mutable.
        reverse(to_may or to_one): An *optional* reverse relationship.
        reverse_type(RelationType): The reverse relationship approach.
        resource_classes(Resource): The kinds of Resources to expect
            in the relationship


    Returns:

        A builder function which, given a source class creates a
        one-to-many relationship with the previously supplied target.

    A to-many relationship means that the there are many *dest_class*
    resources associated with the given source class. The returned
    method builder will automatically create methods for fetching the
    associated objects. If the *reverse* function is supplied the
    builder will create the correponding reverse relationship methods
    on the target class.

    .. code-block:: python

        @to_many(Sensor, writable=True)
        class Label:
            pass

        # find a label, then fetch sensors
        sensor = label.sensors()

    Since the example above also declares that the relationship is
    *writable* you can also add, remove and update all target
    resources from the source object:

    .. code-block:: python

        # fetch a couple of sensors then add them to the label
        label.add_sensors([sensor1, sensor2])

        # remove a sensor from the label
        label.remove_sensors([sensor1])

        # remove all sensors from the label
        label.update_sensors([])

    """
    def method_builder(cls):
        dest_resource_type = dest_class._resource_type()
        dest_method_name = pluralize(dest_resource_type).replace('-', '_')
        doc_variables = {
            'from_class': cls.__name__,
            'to_class': dest_class.__name__,
            'to_name': dest_method_name
        }

        fetch_method_doc = """Fetch the {to_name} associated with this :class:`{from_class}`.

        Returns:

              iterable({to_class}): The {to_name} of :class:`{from_class}`
        """

        def _fetch_relationship_included(self):
            session = self._session
            include = self._include
            if include is None or dest_class not in include:
                # You requested an included relationship that was
                # not originally included
                error = "{} was not included".format(dest_class.__name__)
                raise AttributeError(error)
            included = self._included.get(dest_resource_type)
            mk_one = dest_class._mk_one(session,
                                        resource_classes=resource_classes)
            return [mk_one({'data': entry}) for entry in included]

        def fetch_relationship_include(self, use_included=False):
            if use_included:
                return _fetch_relationship_included(self)
            session = self._session
            id = None if self.is_singleton() else self.id
            url = session._build_url(self._resource_path(), id)
            params = build_request_include([dest_class], None)

            def _process(json):
                included = json.get('included')
                mk_one = dest_class._mk_one(session,
                                            resource_classes=resource_classes)
                return [mk_one({'data': entry}) for entry in included]
            return session.get(url, CB.json(200, _process), params=params)

        def fetch_relationship_direct(self, use_included=False):
            if use_included:
                return _fetch_relationship_included(self)
            session = self._session
            id = None if self.is_singleton() else self.id
            url = session._build_url(self._resource_path(), id,
                                     dest_resource_type)
            process = dest_class._mk_many(session,
                                          resource_classes=resource_classes)
            return session.get(url, CB.json(200, process))

        if type == RelationType.DIRECT:
            fetch_relationship = fetch_relationship_direct
        elif type == RelationType.INCLUDE:
            fetch_relationship = fetch_relationship_include
        else:  # pragma: no cover
            raise ValueError("Invalid RelationType: {}".format(type))

        fetch_relationship.__doc__ = fetch_method_doc

        def add_many(self, resources):
            """Add {to_name} to this :class:`{from_class}`.

            Args:

              resources: A list of :class:`{to_class}` to add

            Returns:

                True if the relationship was mutated, False otherwise
            """
            session, url, json = _build_relatonship(self, dest_resource_type,
                                                    resources)
            return session.post(url, CB.boolean(200, false_code=204),
                                json=json)

        def remove_many(self, resources):
            """Remove {to_name} from this :class:`{from_class}`.

            Args:

              resources: A list of :class:`{to_class}` to remove

            Returns:

                True if the relationship was mutated, False otherwise
            """
            session, url, json = _build_relatonship(self, dest_resource_type,
                                                    resources)
            return session.delete(url, CB.boolean(200, false_code=204),
                                  json=json)

        def update_method(self, resources):
            """Set the {to_name} for this :class:`{from_class}`.

            To remove all {to_name} pass in an empty list.

            Args:

              resources: A list of :class:`{to_class}` to set

            Returns:

                True if successful
            """
            session, url, json = _build_relatonship(self, dest_resource_type,
                                                    resources)
            return session.patch(url, CB.boolean(200), json=json)

        methods = [(dest_method_name, fetch_relationship)]
        if writable:
            methods.extend([
                ('add_{}'.format(dest_method_name), add_many),
                ('remove_{}'.format(dest_method_name), remove_many),
                ('update_{}'.format(dest_method_name), update_method)
            ])
        for name, method in methods:
            method.__doc__ = method.__doc__.format(**doc_variables)
            setattr(cls, name, method)

        if reverse is not None:
            reverse(cls, type=reverse_type)(dest_class)

        return cls

    return method_builder
