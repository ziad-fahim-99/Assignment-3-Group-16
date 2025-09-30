import time, functools
def simple_logger(func):
    #A decorator that logs function calls.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def timeit(func):
    #A decorator that prints elapsed time.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        res = func(*args, **kwargs)
        t1 = time.time()
        print(f"[TIME] {func.__name__} took {t1-t0:.3f}s")
        return res
    return wrapper
