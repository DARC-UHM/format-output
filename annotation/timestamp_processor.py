from datetime import timedelta
from util.functions import parse_datetime

from util.constants import NULL_VAL_STRING


class TimestampProcessor:

    def __init__(self, timestamp: str):
        """ Parses loaded string into datetime object """
        self.timestamp = parse_datetime(timestamp)
        if self.timestamp.microsecond >= 500000:
            self.timestamp = self.timestamp + timedelta(seconds=1)

    def get_formatted_timestamp(self):
        return '{:02}:{:02}:{:02}'.format(self.timestamp.hour, self.timestamp.minute, self.timestamp.second)
