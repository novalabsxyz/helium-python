"""Base Resource behavior."""

from __future__ import unicode_literals
from future.utils import iteritems
from builtins import filter as _filter
from json import dumps as to_json
from . import (
    CB,
    build_request_body,
    build_request_include,
    from_iso_date
)


class Base(object):
    """A base class to deal with json based attributes.

    The base class stores a given json object and dynamically promotes
    requested object attributes from the cached jason data if they
    exist.

    Sub-classes can override methods to promote attribtues on
    construction or lazily, when they're requested

    """

    def __init__(self, json):
        """Create a basic json based object.

        Arguments:

            json(dict): A json dictionary to base attributes on

        """
        super(Base, self).__init__()
        self._json_data = json
        self._update_attributes(json)

    def _update_attributes(self, json):
        """Update attributes on creation."""
        pass

    def _promote_json_attribute(self, attribute, value):
        """Promote a given attribute.

        This base implementation just sets the attribute on this
        resources. Subclasses override this in order to do conversion
        for certain attributes, like timestamps.

        """
        setattr(self, attribute, value)
        return value

    def __getattr__(self, attribute):
        """Get a given missing attribute.

        If the attribute is present in the underlying JSON we get it
        and promote it into the attributes of this resource.

        """
        value = self._json_data.get(attribute, None)
        if value is None:
            value = self._json_data.get(attribute.replace('_', '-'), None)
            if value is None:
                raise AttributeError(attribute)
        return self._promote_json_attribute(attribute, value)


class ResourceMeta(Base):
    """Meta information for a resource.

    Every :class:`Resource` object in the Helium API has an associated
    meta object that represents system information for the given
    resource.

    Most of this information is specific to the given resource, but
    all meta instances have at least a ``created`` and ``updated``
    attribute which are timestamps of when the resource was created
    and last updated, respectively. These timestamps are in ISO8601
    format. To convert them to `datetime`s use the `from_iso_date`
    utility function.

    """


class Resource(Base):
    """The base class for all Helium resources.

    The Helium API uses JSONAPI extensively. The :class:`Resource`
    object provides a number of useful JSONAPI abstractions.

    A resource will at least have an ``id`` attribute, which is
    promoted from the underlying json data on creation.

    A resource can be requested to include relation resources in its
    response using the include request parameter. The ``include``
    argument allows relationship lookups to validate whether the
    relationship was originally requested. You normally don't need to
    specify this since the Resource retrieval methods like ``all`` and
    ``find`` take care of this behavior.

    """

    def __init__(self, json, session, include=None, included=None):
        """Create a Resource.

        Args:

          json(dict): The json to construct the resource from.

          session(Session): The session use for this resource

        Keyword Args:

            include([Resource class]): Resource classes that are included

            included([json]): A list of all included json resources

        """
        self._session = session
        self._include = include
        self._included = included
        super(Resource, self).__init__(json)

    @classmethod
    def _resource_class(cls, data, registry):
        type = data.get('type')
        return registry.get(type)

    @classmethod
    def _mk_one(cls, session,
                singleton=False, include=None, resource_classes=None):
        classes = resource_classes or [cls]
        registry = {clazz._resource_type(): clazz for clazz in classes}

        def func(json):
            included = json.get('included') if include else None
            data = json.get('data')
            result = None
            if data:
                clazz = cls._resource_class(data, registry)
                result = clazz(data, session,
                               include=include, included=included)
                if singleton:
                    setattr(result, '_singleton', True)
            return result
        return func

    @classmethod
    def _mk_many(cls, session, include=None, resource_classes=None):
        classes = resource_classes or [cls]
        registry = {clazz._resource_type(): clazz for clazz in classes}

        def func(json):
            included = json.get('included') if include else None
            data = json.get('data')
            return [cls._resource_class(entry, registry)
                    (entry, session, include=include, included=included)
                    for entry in data]
        return func

    @classmethod
    def all(cls, session, include=None):
        """Get all resources of the given resource class.

        This should be called on sub-classes only.

        The include argument allows relationship fetches to be
        optimized by including the target resources in the request of
        the containing resource. For example::

        .. code-block:: python

            org = Organization.singleton(session, include=[Sensor])
            org.sensors(use_included=True)

        Will fetch the sensors for the authorized organization as part
        of retrieving the organization. The ``use_included`` forces
        the use of included resources and avoids making a separate
        request to get the sensors for the organization.

        Args:

            session(Session): The session to look up the resources in

        Keyword Args:

            incldue: A list of resource classes to include in the
                request.

        Returns:

            iterable(Resource): An iterator over all the resources of
                this type

        """
        return cls.where(session, include=include)

    @classmethod
    def find(cls, session, resource_id, include=None):
        """Retrieve a single resource.

        This should only be called from sub-classes.

        Args:

            session(Session): The session to find the resource in

            resource_id: The ``id`` for the resource to look up

        Keyword Args:

            include: Resource classes to include

        Returns:

            Resource: An instance of a resource, or throws a
              :class:`NotFoundError` if the resource can not be found.

        """
        url = session._build_url(cls._resource_path(), resource_id)
        params = build_request_include(include, None)
        process = cls._mk_one(session, include=include)
        return session.get(url, CB.json(200, process), params=params)

    @classmethod
    def where(cls, session, include=None, metadata=None):
        """Get filtered resources of the given resource class.

        This should be called on sub-classes only.

        The include argument allows relationship fetches to be
        optimized by including the target resources in the request of
        the containing resource. For example::

        .. code-block:: python

            org = Organization.singleton(session, include=[Sensor])
            org.sensors(use_included=True)

        Will fetch the sensors for the authorized organization as part
        of retrieving the organization. The ``use_included`` forces
        the use of included resources and avoids making a separate
        request to get the sensors for the organization.

        The metadata argument enables filtering on resources that
        support metadata filters. For example::

        .. code-block:: puython

            sensors = Sensor.where(session, metadata={ 'asset_id': '23456' })

        Will fetch all sensors that match the given metadata attribute.

        Args:

            session(Session): The session to look up the resources in

        Keyword Args:

            incldue(list): The resource classes to include in the
                request.

            metadata(dict or list): The metadata filter to apply

        Returns:

            iterable(Resource): An iterator over all found resources
                of this type

        """
        url = session._build_url(cls._resource_path())
        params = build_request_include(include, None)
        if metadata is not None:
            params['filter[metadata]'] = to_json(metadata)
        process = cls._mk_many(session, include=include)
        return session.get(url, CB.json(200, process), params=params)

    @classmethod
    def create(cls, session, attributes=None, relationships=None):
        """Create a resource of the resource.

        This should only be called from sub-classes

        Args:

          session(Session): The session to create the resource in.

          attributes(dict): Any attributes that are valid for the
              given resource type.

          relationships(dict): Any relationships that are valid for the
              given resource type.

        Returns:

          Resource: An instance of a resource.

        """
        resource_type = cls._resource_type()
        resource_path = cls._resource_path()
        url = session._build_url(resource_path)
        json = build_request_body(resource_type, None,
                                  attributes=attributes,
                                  relationships=relationships)
        process = cls._mk_one(session)
        return session.post(url, CB.json(201, process), json=json)

    @classmethod
    def singleton(cls, session, include=None):
        """Get the a singleton API resource.

        Some Helium API resources are singletons. The authorized user
        and organization for a given API key are examples of this.

        .. code-block:: python

            authorized_user = User.singleton(session)

        will retrieve the authorized user for the given
        :class:`Session`

        Keyword Args:

            include: Resource classes to include

        """
        params = build_request_include(include, None)
        url = session._build_url(cls._resource_path())
        process = cls._mk_one(session, singleton=True, include=include)
        return session.get(url, CB.json(200, process), params=params)

    @classmethod
    def _resource_type(cls):
        return cls.__name__.lower()

    @classmethod
    def _resource_path(cls):
        return cls._resource_type()

    def _promote_json_attribute(self, attribute, value):
        if attribute == 'meta':
            value = ResourceMeta(value)
        return super(Resource, self)._promote_json_attribute(attribute, value)

    def _update_attributes(self, json):
        super(Resource, self)._update_attributes(json)
        # promote id
        self.id = json.get('id', None)
        # promote all top level attributes
        for (k, v) in iteritems(json.pop('attributes', {})):
            self._promote_json_attribute(k, v)
        # process includes if specified
        if self._include is not None:
            # Look up relationships and the types we were told are included
            relationships = json.pop('relationships', {})
            included_types = [cls._resource_type() for cls in self._include]

            def _filter_included(resource_type):
                # Get the relationship list and store the ids
                related = relationships.get(resource_type, {})
                related = related.get('data', None) or []
                if isinstance(related, dict):
                    # to one relationship
                    related = frozenset([related.get('id')])
                else:
                    related = frozenset([r.get('id') for r in related])

                def _resource_filter(resource):
                    return resource.get('id') in related
                # Filter all included objects for the resources
                return list(_filter(_resource_filter, self._included))

            # Construct a dictionary of filtered included resources
            # and replace the initial stash
            self._included = {type: _filter_included(type)
                              for type in included_types}

    def __eq__(self, other):
        """Check equality with another object."""
        return all([isinstance(other, self.__class__),
                    self.id == other.id])

    def __ne__(self, other):
        """Well this would be the opposite of __eq__."""
        return not self.__eq__(other)

    def __hash__(self):
        """The hash of a resource.

        A resource is always considered unique based on it's uuid
        based ``id``. Since uuids hash particularly well they form a
        nice hash.

        """
        return hash(self.id)

    def __repr__(self):
        """The string representation of the resource."""
        return '<{s.__class__.__name__} {{ id: {s.id} }}>'.format(s=self)

    def is_singleton(self):
        """Whether this instance is a singleton."""
        return hasattr(self, '_singleton')

    def update(self, attributes=None):
        """Update this resource.

        Not all aspects of a resource can be updated. If the server
        rejects updates an error will be thrown.

        Keyword Arguments:

          attributes(dict): Attributes that are to be updated

        Returns:

          Resource: A new instance of this type of resource with the
          updated attribute. On errors an exception is thrown.

        """
        resource_type = self._resource_type()
        resource_path = self._resource_path()
        session = self._session
        singleton = self.is_singleton()
        id = None if singleton else self.id
        url = session._build_url(resource_path, id)
        attributes = build_request_body(resource_type, self.id,
                                        attributes=attributes)
        process = self._mk_one(session, singleton=singleton)
        return session.patch(url, CB.json(200, process), json=attributes)

    def delete(self):
        """Delete the resource.

        Returns:

          True if the delete is successful. Will throw an error if
          other errors occur

        """
        session = self._session
        url = session._build_url(self._resource_path(), self.id)
        return session.delete(url, CB.boolean(204))
