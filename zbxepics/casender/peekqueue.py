from queue import PriorityQueue


class PriorityPeekQueue(PriorityQueue):

    def peek(self):
        return None if self.empty() else self.queue[0]
