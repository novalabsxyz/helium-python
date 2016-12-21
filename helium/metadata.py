"""The metadata resource."""

from __future__ import unicode_literals
from . import Resource, CB, build_request_body


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

    def _publish_metadata(self, publish, attributes):
        session = self._session
        resource_type = self.__class__._resource_type()
        target_resource_path = self._target_resource_path
        target_resource_id = None if self.is_singleton() else self.id
        url = session._build_url(target_resource_path, target_resource_id,
                                 resource_type)
        body = build_request_body(resource_type,
                                  target_resource_id,
                                  attributes=attributes)
        def _process(json):
            data = json.get('data')
            return Metadata(data, session, target_resource_path)
        return publish(url, CB.json(200, _process), json=body)

    def update(self, attributes):
        """Update metadata.

        Updates this metadata with the given attributes. Updating
        means that the given attributes are updated or added to the
        existing metadata instance.

        Keyword Args:

           attributes(dict): A dictionary that can be represented as
                 JSON.

        Returns:

            The updated metadata

        """
        return self._publish_metadata(self._session.patch, attributes)

    def replace(self, attributes):
        """Replace the metadata.

        Replaces this metadata with the given attributes, removing all
        other attribute known to the Helium API for this metadata.

        Keyword Args:

           attributes(dict): A dictionary that can be represented as
                 JSON.

        Returns:

            The replaced metadata

        """
        return self._publish_metadata(self._session.put, attributes)


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

            def _process(json):
                data = json.get('data')
                metadata = Metadata(data, session, resource_path)
                if self.is_singleton():
                    setattr(metadata, '_singleton', True)
                return metadata

            return session.get(url, CB.json(200, _process))

        method.__doc__ = method_doc
        setattr(cls, 'metadata', method)
        return cls

    return method_builder
