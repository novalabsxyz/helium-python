"""Exceptions for the Helium API library."""

from __future__ import unicode_literals


class Error(Exception):
    """The base exception class."""

    def __init__(self, response):
        """Construct an Error.

        :param :class:requests.Response response:
        """
        super(Error, self).__init__(response)
        #: Response code that triggered the error
        self.response = response
        self.code = response.status_code
        self.errors = []
        try:
            error = response.json()
            #: List of errors provided by Helium
            self.errors = error.get('errors', [])
            if len(self.errors) > 0:
                self.msg = self.errors[0].get('detail', '[No message]')
        except:  # pragma: no cover
            self.msg = response.content or '[No message]'

    def __repr__(self):
        return '<{0} [{1}]>'.format(self.__class__.__name__,
                                    self.msg or self.code)

    def __str__(self):
        return '{0} {1} ({r.method} {r.url})'.format(self.code, self.msg,
                                                     r=self.response.request)

    @property
    def message(self):
        """The actual message returned by the API."""
        return self.msg


class NotFoundError(Error):
    pass


class ClientError(Error):
    pass


class ServerError(Error):
    pass

error_classes = {
    404: NotFoundError
}


def error_for(response):
    """Return the appropriate initialized exception class for a response."""
    klass = error_classes.get(response.status_code)
    if klass is None:
        if 400 <= response.status_code < 500:
            klass = ClientError
        if 500 <= response.status_code < 600:
            klass = ServerError  # pragma: no cover
    return klass(response)
