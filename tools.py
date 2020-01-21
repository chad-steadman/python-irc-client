#!/usr/bin/env python
import inspect
import os.path
from datetime import datetime

SEVERITY = {
    'DEBUG': 'DEBUG',
    'INFO': 'INFO',
    'WARN': 'WARN',
    'ERROR': 'ERROR',
    'FATAL': 'FATAL'
}


def println(message, severity=SEVERITY['INFO'], debug_mode=False):
    """Custom print based on message severity.

    Args:
        message -- The message to print.
        severity -- Severity level of the message. 'DEBUG' severity only prints if debug_mode=True. (Default = 'INFO')
        debug_mode -- Suppresses or allows printing of messages with 'DEBUG' severity. (Default = False)
    """
    fname = os.path.basename(inspect.stack()[1].filename)
    timestamp = datetime.now().strftime('%H:%M:%S')

    if severity == SEVERITY['DEBUG'] and debug_mode == False:
        pass
    else:
        print('[{}] [{}] [{}] {}'.format(timestamp, fname, severity, message))
