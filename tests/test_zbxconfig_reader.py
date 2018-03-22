#!/usr/bin/env python

import unittest
import os

from zbxepics.casender import ZabbixConfigReaderJSON


class TestZabbixConfigReader(unittest.TestCase):

    def test_config_reader_json(self):
        dir_path = os.path.dirname(__file__)
        config_file = os.path.join(dir_path, 'test_sender_data.json')
        reader = ZabbixConfigReaderJSON(config_file)
        items = reader.get_items()

        self.assertEqual(len(items), 4)

    def test_config_reader_json_err(self):
        dir_path = os.path.dirname(__file__)
        config_file = os.path.join(dir_path, 'test_sender_data_err.json')
        with self.assertRaises(KeyError):
            ZabbixConfigReaderJSON(config_file)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
