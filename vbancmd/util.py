def cache(func):
    """ check if recently cached was an updated value """
    def wrapper(*args, **kwargs):
        # setup cache check
        res = func(*args, **kwargs)
        # update cache
        return res
    return wrapper