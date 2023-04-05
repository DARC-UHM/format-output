from datetime import timedelta
from util.functions import parse_datetime

from util.constants import NULL_VAL_STRING


class TimestampProcessor:

    def __init__(self, recorded_timestamp: str):
        """ Parses loaded string into datetime object """
        self.recorded_time = parse_datetime(recorded_timestamp)
        if self.recorded_time.microsecond >= 500000:
            self.recorded_time = self.recorded_time + timedelta(seconds=1)

    def get_formatted_timestamp(self):
        return '{:02}:{:02}:{:02}'.format(self.recorded_time.hour, self.recorded_time.minute, self.recorded_time.second)
