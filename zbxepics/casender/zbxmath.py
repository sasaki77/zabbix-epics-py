def last(iterable):
    return iterable[-1]


def avg(iterable):
    sum_ = sum(iterable)
    n = len(iterable)
    return float(sum_) / n
