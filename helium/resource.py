"""Base Resource behavior."""

from __future__ import unicode_literals
from future.utils import iteritems
from . import response_boolean, response_json
from . import build_resource_attributes


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
        pass

    def _promote_json_attribute(self, attribute, value):
        setattr(self, attribute, value)
        return value

    def __getattr__(self, attribute):
        if attribute not in self._json_data:
            raise AttributeError(attribute)
        value = self._json_data.get(attribute, None)
        return self._promote_json_attribute(attribute, value)


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
        url = session._build_url(cls._resource_type())
        json = response_json(session.get(url), 200)
        result = cls(json, session)
        setattr(result, '_singleton', True)
        return result

    @classmethod
    def _resource_type(cls):
        return cls.__name__.lower()

    def _update_attributes(self, json):
        super(Resource, self)._update_attributes(json)
        self.id = json.get('id', None)
        for (k, v) in iteritems(json.pop('attributes', {})):
            self._promote_json_attribute(k, v)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.id is not None and self.id == other.id)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<{s.__class__.__name__} {{ id: {s.id} }}>'.format(s=self)

    @property
    def short_id(self):
        """Get the short version of the UUID for the resource."""
        return self.id.split('-')[0]

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
        klass = self.__class__
        session = self._session
        url = session._build_url(resource_type, self.id)
        attributes = build_resource_attributes(resource_type, self.id, kwargs)
        json = response_json(session.patch(url, json=attributes), 200)
        return klass(json, session)

    def delete(self):
        """Delete the resource.

        Returns:

          True if the delete is successful. Will throw an error if
          other errors occur

        """
        session = self._session
        url = session._build_url(self._resource_type(), self.id)
        return response_boolean(session.delete(url), 204)
