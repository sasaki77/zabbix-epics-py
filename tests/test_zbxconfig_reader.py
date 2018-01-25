#!/usr/bin/env python

import unittest
from zbxepics.zbxconfig import ZabbixConfigReaderJSON


class TestZabbixConfigReader(unittest.TestCase):

    def test_config_reader_json(self):
        reader = ZabbixConfigReaderJSON('test_sender_data.json')
        items = reader.get_items()

        self.assertEqual(len(items), 4)

    def test_config_reader_json_err(self):
        with self.assertRaises(KeyError):
            ZabbixConfigReaderJSON('test_sender_data_err.json')


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
