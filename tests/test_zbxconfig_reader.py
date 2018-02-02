#!/usr/bin/env python

import unittest
import os

from zbxepics.zbxconfig import ZabbixConfigReaderJSON


class TestZabbixConfigReader(unittest.TestCase):

    def test_config_reader_json(self):
        config_file = '/'.join([os.path.dirname(__file__),
                                'test_sender_data.json'])
        reader = ZabbixConfigReaderJSON(config_file)
        items = reader.get_items()

        self.assertEqual(len(items), 4)

    def test_config_reader_json_err(self):
        config_file = '/'.join([os.path.dirname(__file__),
                                'test_sender_data_err.json'])
        with self.assertRaises(KeyError):
            ZabbixConfigReaderJSON(config_file)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
