import unittest
from utils import get_schedule


class TestGetScheduleFunction(unittest.TestCase):

    def test_basic_case(self):
        data = {'Event A': 2}
        result = get_schedule(data)
        self.assertEqual(result, {'Event A': [10, 12]})

    def test_multiple_events(self):
        data = {'Event A': 2, 'Event B': 3, 'Event C': 1}
        result = get_schedule(data)
        self.assertEqual(result, {'Event A': [20, 22], 'Event C': [10, 11], 'Event B': [14, 17]})

    def test_no_free_time(self):
        data = {'Event A': 10, 'Event B': 6}
        with self.assertRaises(OverflowError):
            get_schedule(data)

    def test_long_events_with_free_time(self):
        data = {'Event A': 5, 'Event B': 2, 'Event C': 4}
        result = get_schedule(data)
        self.assertEqual(result, {'Event A': [13, 18], 'Event B': [10, 12], 'Event C': [19, 23]})

    def test_empty_data(self):
        data = {}
        result = get_schedule(data)
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
