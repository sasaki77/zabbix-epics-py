from queue import PriorityQueue


class PriorityPeekQueue(PriorityQueue):
    """PriorityPeekQueue class, extended PriorityQueue class."""

    def peek(self):
        """Return the first data.

        If the queue is empty, None is returned.
        """
        return None if self.empty() else self.queue[0]
