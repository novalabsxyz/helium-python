"""Helium Timeseries functionality."""

from __future__ import unicode_literals

from . import Resource, response_json, response_boolean
from . import to_iso_date
from . import build_request_attributes
from . import LiveSession
from collections import Iterable, namedtuple


AggregateValue = namedtuple('agg', ['min', 'max', 'avg'])
AggregateValue.__new__.__defaults__ = (None,) * len(AggregateValue._fields)


class DataPoint(Resource):
    """Data points for timeseries.

    A datapint represents readings for a given :class:`Timeseries`
    instance and will always have at least the following attributes:

    :port: The port for the datapoint represents a user or system
        defined hint around what the value means

    :value: The actual reading value, this can be any json value

    :timestamp: An ISO8601 timestamp representing the time the
        reading was taken

    """
    def __init__(self, json, session, **kwargs):
        self._is_aggregate = kwargs.pop("is_aggregate", False)
        super(DataPoint, self).__init__(json, session, **kwargs)

    @classmethod
    def _resource_type(cls):
        return "timeseries"

    def _promote_json_attribute(self, attribute, value):
        if attribute == 'value' and self._is_aggregate:
            value = AggregateValue(**value)
        super(DataPoint, self)._promote_json_attribute(attribute, value)


class Timeseries(Iterable):
    """A timeseries readings container.

    Objects of this class represents a single timeseries query. A
    Timeseries instance will automatically page forward or backward
    through the pages returned from the Helium API to return data
    points that fit within the given arguments.

    The timeseries instance is an :class:`Iterable` which can be used
    to lazily iterate over very large timeseries data sets. The
    returned timeseries object will not actually start making any
    requests to the Helium API until you start iterating over it.

    For example, given:

    .. code-block:: python

        @timeseries()
        class Sensor(Resource):
            pass

    You can request a timeseries using:

    .. code-block:: python

        from itertools import islice

        # Fetch a sensor
        timeseries = sensor.timeseries()

        # Get the first 10 readings
        first10 = list(islice(timeseries, 10))

    Note that each call to ``sensor.timeseries()`` will return a new
    timeseries object which you can iterate over.

    You can filter timeseries data by specifying ``port``, ``start``
    or ``end`` dates. Note that start and end dates support a relaxed
    form of ISO8601:

    .. code-block:: pytnon

        timeseries = sensor.timeseries(start='2016-09-01',
                                       end='2016-04-07T19:12:06Z')


    You can aggregate numeric timeseries data by specifying
    ``agg_type`` and ``agg_size``. For example, to aggregate minimum,
    maximum and average temperature readings in 6 hour buckets:

    .. code-block:: python

        timeseries = sensor.timeseries(agg_type='min,max,avg',
                                       agg_size='6h',
                                       port='t')

    The resulting data points will have an aggregate value that will
    contain the requested aggregates as attributes:

    .. code-block:: python

        first = list(islice(timeseries, 1))[0]
        print(first.value.min)


    Args:

        session(Session): The session to use for timeseries requests

        resource_class(Resource): The Resource subclass class to fetch
            timeseries for

        resource_id(uuid): Id of the resource (if applicable) to fetch
            timeseries for

    Keyword Args:

        datapoint_class(Resource): The class to use to construct datapoints

        datapoint_id(uuid): The datapoint id to start the timeseries

        page_size(int): The size of pages to fetch (defaults to server
            preference)

        port(string): The port name to filter readings on

        start(string): Start date for timeseries (inclusive)

        end(string): End date for timeseries (exclusive)

        agg_size(string): The size of the aggregation bucket

        agg_type(string): The list of aggregations to perform

        direction("prev" or "next"): Whether to go backward ("prev") or
            forward ("next") in time

    """

    def __init__(self, session, resource_class, resource_id,
                 datapoint_class=DataPoint,
                 datapoint_id=None,
                 page_size=None,
                 direction='prev',
                 start=None,
                 end=None,
                 agg_size=None,
                 agg_type=None,
                 port=None):
        self._session = session
        self._datapoint_class = datapoint_class

        self._resource_class = resource_class
        self._base_url = session._build_url(resource_class._resource_type(),
                                            resource_id,
                                            'timeseries')
        self._resource_id = resource_id
        self._direction = direction
        self._is_aggregate = False

        params = {}
        if datapoint_id is not None:
            params['page[id]'] = datapoint_id
        if page_size is not None:
            params['page[size]'] = page_size
        if port is not None:
            params['filter[port]'] = port
        if start is not None:
            params['filter[start]'] = start
        if end is not None:
            params['filter[end]'] = end
        if agg_type is not None:
            self._is_aggregate = True
            params['agg[type]'] = agg_type
        if agg_size is not None:
            self._is_aggregate = True
            params['agg[size]'] = agg_size
        self._params = params

    def __iter__(self):
        """Construct an iterator for this timeseries."""
        session = self._session
        datapoint_class = self._datapoint_class
        direction = self._direction
        params = self._params
        is_aggregate = self._is_aggregate

        def _get_json(url):
            json = response_json(session.get(url, params=params), 200,
                                 extract=None)
            data = json.get('data')
            link = json.get('links')
            link = link.get(direction)
            return (json, data, link)

        json, data, url = _get_json(self._base_url)

        finished = False
        while not finished:
            for entry in data:
                datapoint = datapoint_class(entry, session,
                                            is_aggregate=is_aggregate)
                yield datapoint

            if url is None:
                finished = True
            else:
                json, data, url = _get_json(url)

    def create(self, port, value, timestamp=None):
        """Post a new reading to a timeseries.

        A reading is comprised of a `port`, a `value` and a timestamp.

        A port is like a tag for the given reading and gives an
        indication of the meaning of the value.

        The value of the reading can be any valid json value.

        The timestamp is considered the time the reading was taken, as
        opposed to the `created` time of the data-point which
        represents when the data-point was stored in the Helium
        API. If the timestamp is not given the server will construct a
        timestemp upon receiving the new reading.

        Args:

            port(string): The port to use for the new data-point
            value: The value for the new data-point

        Keyword Args:

            timestamp(:class:`datetime`): An optional :class:`datetime` object

        """
        session = self._session
        datapoint_class = self._datapoint_class
        attributes = {
            'port': port,
            'value': value,
        }
        if timestamp is not None:
            attributes['timestamp'] = to_iso_date(timestamp)
        attributes = build_request_attributes('data-point', None, attributes)
        data = session.post(self._base_url, json=attributes)
        return datapoint_class(response_json(data, 201), session)

    def live(self):
        """Get a live stream of timeseries readings.

        This returns an Iterable over a live stream of readings. Note
        that the result will need to be closed since the system can
        not tell when you'll be done with it.

        You can either call ``close`` on the endpoint when you're done
        with it or use the handy ``contextlib.closing`` function:


        .. code-block:: python

            from contextlib import closing

            # Fetch a sensor
            timeseries = sensor.timeseries()

            # ensure live endpoint closed
            with closing(timeseries.live()) as live:
                # Wait for 10 readings
                first10 = list(islice(live, 10))

        Returns:



        """
        session = self._session
        datapoint_class = self._datapoint_class
        is_aggregate = self._is_aggregate
        url = "{}/live".format(self._base_url)
        headers = {
            'Accept': 'text/event-stream'
        }
        response = session.get(url, stream=True, headers=headers)
        response_boolean(response, 200)
        return LiveSession(response, session, datapoint_class,
                           is_aggregate=is_aggregate)


def timeseries():
    """Create a timeseries builder.

    Returns:

        A builder function which, given a class creates a timeseries
        relationship for that class.

    """
    def method_builder(cls):
        method_doc = """Fetch the timeseries for this :class:`{0}`.

        Returns:

            The :class:`Timeseries` for this :class:`{0}`

        Keyword Args:

            **kwargs: The :class:`Timeseries` object constructor arguments.
        """.format(cls.__name__)

        def method(self, **kwargs):
            resource_id = None if self.is_singleton() else self.id
            return Timeseries(self._session, cls, resource_id, **kwargs)

        method.__doc__ = method_doc
        setattr(cls, 'timeseries', method)
        return cls
    return method_builder
