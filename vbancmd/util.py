from pathlib import Path

PROJECT_DIR = str(Path(__file__).parents[1])


def project_path():
    return PROJECT_DIR


def cache(func):
    """check if recently cached was an updated value"""

    def wrapper(*args, **kwargs):
        # setup cache check
        res = func(*args, **kwargs)
        # update cache
        return res

    return wrapper


def script(func):
    """Convert dictionary to script"""

    def wrapper(*args):
        remote, script = args
        if isinstance(script, dict):
            params = ""
            for key, val in script.items():
                obj, m2, *rem = key.split("-")
                index = int(m2) if m2.isnumeric() else int(*rem)
                params += ";".join(
                    f"{obj}{f'.{m2}stream' if not m2.isnumeric() else ''}[{index}].{k}={int(v) if isinstance(v, bool) else v}"
                    for k, v in val.items()
                )
                params += ";"
            script = params
        return func(remote, script)

    return wrapper
