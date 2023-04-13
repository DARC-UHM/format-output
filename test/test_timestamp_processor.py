import pytest
from datetime import datetime
from annotation.timestamp_processor import TimestampProcessor


class TestTimestampProcessor:

    def test_init(self):
        test_timestamp = TimestampProcessor('2014-09-05T14:08:41Z')
        assert test_timestamp.timestamp == datetime(2014, 9, 5, 14, 8, 41)

    def test_init_round_down(self):
        test_timestamp = TimestampProcessor('2014-09-05T14:08:41.492Z')
        assert test_timestamp.timestamp == datetime(2014, 9, 5, 14, 8, 41)

    def test_init_round_up(self):
        test_timestamp = TimestampProcessor('2014-09-05T14:08:41.592Z')
        assert test_timestamp.timestamp == datetime(2014, 9, 5, 14, 8, 42)

    def test_init_fail(self):
        with pytest.raises(Exception):
            TimestampProcessor('not a timestamp')

    def test_get_formatted_timestamp(self):
        test_timestamp = TimestampProcessor('2014-09-05T14:08:41Z')
        assert test_timestamp.get_formatted_timestamp() == '14:08:41'
