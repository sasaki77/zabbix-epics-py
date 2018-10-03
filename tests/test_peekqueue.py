from zbxepics.casender.peekqueue import PriorityPeekQueue


def test_peekqueue_init():
    q = PriorityPeekQueue()
    assert q is not None


def test_peek_queue_refer():
    """
    Test for refer to elements with the highest priority
     without removing them.
    """
    q = PriorityPeekQueue()
    for val in range(5):
        q.put(val)

    peek_value = q.peek()
    assert peek_value == 0
    assert q.qsize() == 5


def test_peek_queue_err():
    q = PriorityPeekQueue()
    peek_value = q.peek()

    assert peek_value is None
