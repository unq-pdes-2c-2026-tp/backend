import time
from functools import wraps

from opentelemetry.metrics import Histogram


def measure_time(histogram: Histogram):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            histogram.record(end - start, attributes={"func": func.__name__})
            return result

        return wrapper

    return decorator
