from queue import PriorityQueue


class PriorityPeekQueue(PriorityQueue):

    def peek(self):
        if not self.empty():
            return self.queue[0]
        else:
            return None
