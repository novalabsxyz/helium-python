"""Base Resource behavior."""

from __future__ import unicode_literals
from future.utils import iteritems
from builtins import filter as _filter
from . import response_boolean, response_json
from . import build_request_attributes, build_request_include
from . import from_iso_date


class Base(object):
    """A base class to deal with json based attributes.

    The base class stores a given json object and dynamically promotes
    requested object attributes from the cached jason data if they
    exist.

    Sub-classes can override methods to promote attribtues on
    construction or lazily, when they're requested

    Arguments:

        json(dict): A json dictionary to base attributes on

    """

    def __init__(self, json):
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
    and last updated, respectively.

    """

    def _promote_json_attribute(self, attribute, value):
        if attribute == 'created':
            value = from_iso_date(value)
        elif attribute == 'updated':
            value = from_iso_date(value)
        return super(ResourceMeta, self)._promote_json_attribute(attribute,
                                                                 value)


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

    Args:

      json(dict): The json to construct the resource from.

      session(Session): The session use for this resource

    Keyword Args:

        include([Resource class]): Resource classes that are included

        included([json]): A list of all included json resources

    """

    def __init__(self, json, session, include=None, included=None):
        self._session = session
        self._include = include
        self._included = included
        super(Resource, self).__init__(json)

    @classmethod
    def _mk_one(cls, session, json, singleton=False, include=None):
        included = json.get('included') if include else None
        data = json.get('data')
        result = cls(data, session, include=include, included=included)
        if singleton:
            setattr(result, '_singleton', True)
        return result

    @classmethod
    def _mk_many(cls, session, json, include=None):
        included = json.get('included') if include else None
        data = json.get('data')
        return [cls(entry, session, include=include, included=included)
                for entry in data]

    @classmethod
    def all(cls, session, include=None):
        """Get all resources of the given resource class.

        This should be called on sub-classes only.

        The include argument allows relationship fetches to be
        optimized by including the target resources in the request of
        the containing resource. For example::

        .. code-block:: python

            org = Organization.singleton(include=[Sensor])
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
        url = session._build_url(cls._resource_path())
        params = build_request_include(include, None)
        json = response_json(session.get(url, params=params), 200,
                             extract=None)
        return cls._mk_many(session, json, include=include)

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
        json = response_json(session.get(url, params=params), 200,
                             extract=None)
        return cls._mk_one(session, json, include=include)

    @classmethod
    def create(cls, session, **kwargs):
        """Create a resource of the resource.

        This should only be called from sub-classes

        Args:

          session(Session): The session to create the resource in.

          kwargs: Any attributes that are valid for the given resource type.

        Returns:

          Resource: An instance of a resource.

        """
        resource_type = cls._resource_type()
        resource_path = cls._resource_path()
        url = session._build_url(resource_path)
        attributes = build_request_attributes(resource_type, None, kwargs)
        json = response_json(session.post(url, json=attributes), 201,
                             extract=None)
        return cls._mk_one(session, json)

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
        json = response_json(session.get(url, params=params), 200,
                             extract=None)
        return cls._mk_one(session, json, singleton=True, include=include)

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
                related = relationships.get(resource_type, {}).get('data', None) or []
                if isinstance(related, dict):
                    # to one relationship
                    related = [related.get('id')]
                else:
                    related = frozenset([r.get('id') for r in related])

                def _resource_filter(resource):
                    if resource.get('type') != resource_type:
                        return False
                    return resource.get('id') in related
                # Filter all included objects for the resource type
                # and whether they're related to this resource
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

    def update(self, **kwargs):
        """Update attributes of this resource.

        Not all attributes can be updated. If the server rejects
        attribute updates an error will be thrown.

        Keyword Arguments:

          kwargs: Attributes that are to be updated

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
        attributes = build_request_attributes(resource_type, self.id, kwargs)
        json = response_json(session.patch(url, json=attributes), 200,
                             extract=None)
        return self._mk_one(session, json, singleton=singleton)

    def delete(self):
        """Delete the resource.

        Returns:

          True if the delete is successful. Will throw an error if
          other errors occur

        """
        session = self._session
        url = session._build_url(self._resource_path(), self.id)
        return response_boolean(session.delete(url), 204)
