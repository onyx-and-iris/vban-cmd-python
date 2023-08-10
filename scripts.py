import os
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


def test_basic():
    os.environ["KIND"] = "basic"
    subprocess.run(["tox"])


def test_banana():
    os.environ["KIND"] = "banana"
    subprocess.run(["tox"])


def test_potato():
    os.environ["KIND"] = "potato"
    subprocess.run(["tox"])


def test_all():
    steps = [test_basic, test_banana, test_potato]
    [step() for step in steps]
