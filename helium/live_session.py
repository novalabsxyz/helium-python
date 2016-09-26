from collections import Iterable
from json import loads as load_json


class LiveSession(Iterable):
    """Represents a live SSE endpoint as an Iterable.

    Keyword Args:

        response(Response): The response to a live endpoint request

        session(Session): The session with Helium

        resource_class(Resource): The class of resource to constructx
    """
    _FIELD_SEPARATOR = ':'

    def __init__(self, response, session, resource_class, **resource_args):
        self._response = response
        self._session = session
        self._resource_class = resource_class
        self._resource_args = resource_args

    def _read(self, response):
        data = ""
        for line in response.iter_lines(decode_unicode=True):
            if not line.strip():
                yield data
                data = ""
            data = data + "\n" + line

    def __iter__(self):
        resource_class = self._resource_class
        resource_args = self._resource_args
        session = self._session
        response = self._response

        for chunk in self._read(response):
            event_data = ""
            for line in chunk.splitlines():
                # Ignore empty lines
                if not line.strip():
                    continue

                data = line.split(self._FIELD_SEPARATOR, 1)
                field = data[0]
                data = data[1]

                if field == 'data':
                    event_data += data

            if not event_data:
                # Don't report on events with no data
                continue

            event_data = load_json(event_data).get('data')
            yield resource_class(event_data, session, **resource_args)

    def close(self):
        """Close the live session."""
        self._response.close()
