from queue import PriorityQueue


class PriorityPeekQueue(PriorityQueue):

    def peek(self):
        return self.queue[0]
