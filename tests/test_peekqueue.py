#!/usr/bin/env python

import unittest
from zbxepics.casender.peekqueue import PriorityPeekQueue


class TestPriorityPeekQueue(unittest.TestCase):

    def test_peek_queue(self):
        """
        Test for refer to elements with the highest priority
         without removing them.
        """
        q = PriorityPeekQueue()
        q.put(1)
        q.put(2)
        q.put(3)

        peek_value = q.peek()
        self.assertEqual(peek_value, 1)
        self.assertEqual(q.qsize(), 3)

    def test_peek_queue_err(self):
        with self.assertRaises(IndexError):
            q = PriorityPeekQueue()
            q.peek()


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
