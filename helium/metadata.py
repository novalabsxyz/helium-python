"""The metadata resource."""

from __future__ import unicode_literals
from . import Resource, response_json, build_request_attributes


class Metadata(Resource):
    """Arbitrary JSON store for resources.

    When a :class:`Resource` declares a Metadata relationship:

    .. code-block: python

            @metadata()
            class Organization(Resource)
                pass

    The corresponding resource has a ``metadata`` method to fetch a
    metadata object. This metadata object is an arbitrary store for
    JSON data that can be updated or replaced.

    Updating the metadata means adding or changing existing attributes
    in the JSON object.

    Replacing the metadata replaces the entire JSON object with the
    given value.

    """

    def __init__(self, json, session, target_resource_path):
        super(Metadata, self).__init__(json, session)
        self._target_resource_path = target_resource_path

    def _publish_metadata(self, publish, **kwargs):
        session = self._session
        resource_type = self.__class__._resource_type()
        target_resource_path = self._target_resource_path
        target_resource_id = None if self.is_singleton() else self.id
        url = session._build_url(target_resource_path, target_resource_id,
                                 resource_type)
        attributes = build_request_attributes(resource_type,
                                              target_resource_id,
                                              kwargs)
        data = publish(url, json=attributes)
        return Metadata(response_json(data, 200), session,
                        target_resource_path)

    def update(self, **kwargs):
        """Update metadata.

        Updates this metadata with the given attributes. Updating
        means that the given attributes are updated or added to the
        existing metadata instance.

        Keyword Args:

           **kwargs: Any set of keyword arguments that can be
                 represented as JSON.

        Returns:

            The updated metadata

        """
        return self._publish_metadata(self._session.patch, **kwargs)

    def replace(self, **kwargs):
        """Replace the metadata.

        Replaces this metadata with the given attributes, removing all
        other attribute known to the Helium API for this metadata.

        Keyword Args:

           **kwargs: Any set of keyword arguments that can be
                 represented as JSON.

        Returns:

            The replaced metadata

        """
        return self._publish_metadata(self._session.put, **kwargs)


def metadata():
    """Create a metadata method builder.

    Returns:

        A builder function that, given a class, creates a metadata
        relationship for that class.
    """
    def method_builder(cls):
        method_doc = """Fetch the metadata for this :class:`{0}`.

        Returns:

            The :class:`Metadata` for this :class:`{0}`
        """.format(cls.__name__)

        def method(self):
            session = self._session
            resource_id = None if self.is_singleton() else self.id
            resource_path = cls._resource_path()
            url = session._build_url(resource_path, resource_id, 'metadata')
            data = session.get(url)
            return Metadata(response_json(data, 200), session, resource_path)

        method.__doc__ = method_doc
        setattr(cls, 'metadata', method)
        return cls

    return method_builder
