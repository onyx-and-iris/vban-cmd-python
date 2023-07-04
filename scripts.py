import subprocess
import sys
from pathlib import Path


def ex_gui():
    scriptpath = Path.cwd() / "examples" / "gui" / "."
    subprocess.run([sys.executable, str(scriptpath)])


def ex_obs():
    scriptpath = Path.cwd() / "examples" / "obs" / "."
    subprocess.run([sys.executable, str(scriptpath)])


def ex_observer():
    scriptpath = Path.cwd() / "examples" / "observer" / "."
    subprocess.run([sys.executable, str(scriptpath)])


def test():
    subprocess.run(["tox"])
