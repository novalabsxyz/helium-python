"""Base Resource behavior."""

from __future__ import unicode_literals
from future.utils import iteritems
from .exceptions import error_for


class Base(object):
    """The base class for all things that relate to a Helium session."""

    def __init__(self, json, session):
        super(Base, self).__init__()
        self._session = session
        self._json_data = json
        self._update_attributes(json)

    def _update_attributes(self, json):
        pass

    def __getattr__(self, attribute):
        if attribute not in self._json_data:
            raise AttributeError(attribute)
        value = self._json_data.get(attribute, None)
        setattr(self, attribute, value)
        return value

    @classmethod
    def _boolean(cls, response, true_code):
        if response is not None:
            status_code = response.status_code
            if status_code == true_code:
                return True
            raise error_for(response)

    @classmethod
    def _json(cls, response, status_code, extract='data'):
        ret = None
        if cls._boolean(response, status_code) and response.content:
            ret = response.json().get(extract)
        return ret


class Resource(Base):
    """The base class for all Helium resources.

    The Helium API uses JSONAPI extensively. The :class:`Resource`
    object provides a number of useful JSONAPI abstractions.

    A resource will at least have ``id``, ``created`` and ``updated``
    attributes. Any other JSONAPI ``attributes`` in the given json are
    promoted to object attributes

    Args:

      json(dict): The json to construct the resource from.
      session(Session): The session use for this resource

    """

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
        json = cls._json(session.get(url), 200)
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
        json = cls._json(session.get(url), 200)
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
        attributes = session._build_attributes(resource_type, None, kwargs)
        json = cls._json(session.post(url, json=attributes), 201)
        return cls(json, session)

    @classmethod
    def singleton(cls, session):
        url = session._build_url(cls._resource_type())
        json = cls._json(session.get(url), 200)
        result = cls(json, session)
        setattr(result, '_singleton', True)
        return result

    @classmethod
    def _resource_type(cls):
        return cls.__name__.lower()

    def _update_attributes(self, json):
        super(Resource, self)._update_attributes(json)
        self.id = json.get('id', None)
        meta = json.get('meta', None)
        if meta is not None:
            self.created = meta.get('created')
            self.updated = meta.get('updated')
        for (k, v) in iteritems(json.pop('attributes', {})):
            setattr(self, k, v)

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
        attributes = session._build_attributes(resource_type, self.id, kwargs)
        json = klass._json(session.patch(url, json=attributes), 200)
        return klass(json, session)

    def delete(self):
        """Delete the resource.

        Returns:

          True if the delete is successful. Will throw an error if
          other errors occur

        """
        session = self._session
        url = session._build_url(self._resource_type(), self.id)
        return self._boolean(session.delete(url), 204)
