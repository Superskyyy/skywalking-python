import io
import logging
import traceback


class E2EProviderFormatter(logging.Formatter):
    """
    User defined formatter should in no way be
    interfered by the log reporter formatter.
    """

    def format(self, record):
        result = super().format(record)
        return f'e2e_provider:={result}'

    def formatException(self, ei):  # noqa
        """
        Mock user defined formatter which limits the traceback depth
        to None -> meaning it will not involve trackback at all.
        but the agent should still be able to capture the traceback
        at default level of 5 by ignoring the cache.
        """
        sio = io.StringIO()
        tb = ei[2]
        traceback.print_exception(ei[0], ei[1], tb, None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == '\n':
            s = s[:-1]
        return s
