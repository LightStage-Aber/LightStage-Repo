import time


class MyTimer():
    """
    A context manager for simple benchmarking.
    Usage:
        from time_utils.timer import MyTimer
        with MyTimer():
            print(range(9999999))

    Source: https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code/
    """
    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = 'The function took {time} seconds to complete'
        print(msg.format(time=runtime))
