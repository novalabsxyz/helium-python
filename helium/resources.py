from __future__ import unicode_literals
from future.utils import iteritems

from .exceptions import error_for


class Base(object):
    """The base class for all things that relate to a Helium session.
    """

    def __init__(self, json, session):
        super(Base, self).__init__()
        self.session = session
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
            if status_code >= 400:
                raise error_for(response)
        return False

    @classmethod
    def _json(cls, response, status_code):
        ret = None
        if cls._boolean(response, status_code) and response.content:
            ret = response.json().get('data')
        return ret


class Resource(Base):
    """The base class for all Helium resources.

    The Helium API uses JSONAPI extensively. The :class:`Resource`
    object provides a number of useful JSONAPI abstractions.

    A resource will at least have ``id``, ``created`` and ``updated``
    attributes. Any other JSONAPI ``attributes`` in the given json are
    promoted to object attributed

    Args:
      json(dict): The json to construct the resource from.
      session(Session): The session use for this resource

    """

    @classmethod
    def all(cls, session):
        """Get all resources of the given resource class. This should be
        called on sub-classes only.

        Args:
          session(Session): The session to look up the resources in
        """
        url = session._build_url(cls._resource_type())
        response = session.get(url)
        json = cls._json(response, 200)
        return [cls(entry, session) for entry in json]

    @classmethod
    def find(cls, session, resource_id):
        """Retrieve a single resource. This should only be called from
        sub-classes.

        Args:
          session(Session): The session to find the resource in
          resource_id: The ``id`` for the resource to look up

        Returns: An instance of a resource, or throws a
          :class:`NotFoundError` if the resource can not be found.

        """
        url = session._build_url(cls._resource_type(), resource_id)
        response = session.get(url)
        json = cls._json(response, 200)
        return cls(json, session)

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
        """Get the short version of the UUID for the resource.
        """
        return self.id.split('-')[0]


class Sensor(Resource):
    def _update_attributes(self, json):
        super(Sensor, self)._update_attributes(json)
        self.name = json.get('name')


class Label(Resource):
    def _update_attributes(self, json):
        super(Label, self)._update_attributes(json)
        self.name = json.get('name')
