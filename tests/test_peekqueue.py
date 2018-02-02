#!/usr/bin/env python

import unittest

from zbxepics.casender.peekqueue import PriorityPeekQueue


class TestPriorityPeekQueue(unittest.TestCase):

    def testA_init(self):
        q = PriorityPeekQueue()
        self.assertIsNotNone(q)

    def test_peek_queue(self):
        """
        Test for refer to elements with the highest priority
         without removing them.
        """
        q = PriorityPeekQueue()
        for val in range(5):
            q.put(val)

        peek_value = q.peek()
        self.assertEqual(peek_value, 0)
        self.assertEqual(q.qsize(), 5)

    def test_peek_queue_err(self):
        q = PriorityPeekQueue()
        peek_value = q.peek()

        self.assertIsNone(peek_value)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
