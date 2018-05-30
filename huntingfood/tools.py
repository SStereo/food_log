# required for custom date url parameter for the dietplan get endpoint per day
from werkzeug.routing import BaseConverter, ValidationError
# Required to convert time zone aware date strings from Json into a date object
import dateutil.parser

# TODO: Use marshmallow to deserialize data from Post requests
# example: http://marshmallow.readthedocs.io/en/latest/examples.html


def str_to_bool(s):
    """ Required for passing boolean values from html via Ajax to the backend
    """
    if (s == 'True') or (s == 'true'):
        return True
    elif (s == 'False') or (s == 'false'):
        return False
    elif (s == '') or (s is None):
        return None
    else:
        raise ValueError


def str_to_numeric(s):
    """ Required for handling none values correctly
    """
    if s is None:
        s = None
        return s
    elif s == '':
        s = None
        return s
    elif not (s.isnumeric()):
        s = None
        return s
    elif (s.isnumeric()):
        if s.isdigit():
            return int(s)
        else:
            return float(s)
    else:
        raise ValueError


def str_to_date(s):
    """ Required for handling none values correctly
    """
    if s is None:
        s = None
        return s
    elif s == '':
        s = None
        return s
    else:
        s = dateutil.parser.parse(s)
        return s

# Custom url date parameter converter for dietplan per day get method
# TODO: Delete this in case it is not longer needed
class DateConverter(BaseConverter):
    """Extracts a ISO8601 date from the path and validates it."""

    regex = r'\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')
