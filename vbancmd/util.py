from pathlib import Path

PROJECT_DIR = str(Path(__file__).parents[1])

def project_path():
    return PROJECT_DIR

def cache(func):
    """ check if recently cached was an updated value """
    def wrapper(*args, **kwargs):
        # setup cache check
        res = func(*args, **kwargs)
        # update cache
        return res
    return wrapper