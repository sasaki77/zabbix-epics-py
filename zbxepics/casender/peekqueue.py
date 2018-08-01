from queue import PriorityQueue


class PriorityPeekQueue(PriorityQueue):
    """PriorityQueue class with peek method"""

    def peek(self):
        """Return the first data.

        Returns
        -------
        obj
            the head of this queue.
            If the queue is empty, None is returned.
        """

        return None if self.empty() else self.queue[0]
