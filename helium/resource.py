"""Base Resource behavior."""

from __future__ import unicode_literals
from future.utils import iteritems
from . import response_boolean, response_json
from . import build_resource_attributes, from_iso_date


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

    Args:

      json(dict): The json to construct the resource from.
      session(Session): The session use for this resource

    """

    def __init__(self, json, session):
        self._session = session
        super(Resource, self).__init__(json)

    @classmethod
    def all(cls, session):
        """Get all resources of the given resource class.

        This should be called on sub-classes only.

        Args:

          session(Session): The session to look up the resources in

        Returns:

          iterable(Resource): An iterator over all the resources of
        this type

        """
        url = session._build_url(cls._resource_type())
        json = response_json(session.get(url), 200)
        return [cls(entry, session) for entry in json]

    @classmethod
    def find(cls, session, resource_id):
        """Retrieve a single resource.

        This should only be called from sub-classes.

        Args:

          session(Session): The session to find the resource in
          resource_id: The ``id`` for the resource to look up

        Returns:

          Resource: An instance of a resource, or throws a
          :class:`NotFoundError` if the resource can not be found.

        """
        url = session._build_url(cls._resource_type(), resource_id)
        json = response_json(session.get(url), 200)
        return cls(json, session)

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
        url = session._build_url(resource_type)
        attributes = build_resource_attributes(resource_type, None, kwargs)
        json = response_json(session.post(url, json=attributes), 201)
        return cls(json, session)

    @classmethod
    def singleton(cls, session):
        """Get the a singleton API resource.

        Some Helium API resources are singletons. The authorized user
        and organization for a given API key are examples of this.

        .. code-block:: python

            authorized_user = User.singleton(session)

        will retrieve the authorized user for the given
        :class:`Session`

        """
        url = session._build_url(cls._resource_type())
        json = response_json(session.get(url), 200)
        result = cls(json, session)
        setattr(result, '_singleton', True)
        return result

    @classmethod
    def _resource_type(cls):
        return cls.__name__.lower()

    def _promote_json_attribute(self, attribute, value):
        if attribute == 'meta':
            value = ResourceMeta(value)
        return super(Resource, self)._promote_json_attribute(attribute, value)

    def _update_attributes(self, json):
        super(Resource, self)._update_attributes(json)
        self.id = json.get('id', None)
        for (k, v) in iteritems(json.pop('attributes', {})):
            self._promote_json_attribute(k, v)
        self._promote_json_attribute('meta', json.pop('meta', {}))

    def __eq__(self, other):
        """Check equality with another object."""
        return (isinstance(other, self.__class__) and
                self.id is not None and self.id == other.id)

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
        session = self._session
        id = None if hasattr(self, '_singleton') else self.id
        url = session._build_url(resource_type, id)
        attributes = build_resource_attributes(resource_type, self.id, kwargs)
        json = response_json(session.patch(url, json=attributes), 200)
        return self.__class__(json, session)

    def delete(self):
        """Delete the resource.

        Returns:

          True if the delete is successful. Will throw an error if
          other errors occur

        """
        session = self._session
        url = session._build_url(self._resource_type(), self.id)
        return response_boolean(session.delete(url), 204)
