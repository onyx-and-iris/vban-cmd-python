import subprocess
from pathlib import Path


def ex_obs():
    path = Path.cwd() / "examples" / "obs" / "."
    subprocess.run(["py", str(path)])


def ex_observer():
    path = Path.cwd() / "examples" / "observer" / "."
    subprocess.run(["py", str(path)])
