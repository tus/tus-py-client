"""Smoke checks for checked-in examples."""

import py_compile
from pathlib import Path


def test_api2_devdock_examples_compile():
    examples_root = Path(__file__).parent.parent / "examples"
    for example in examples_root.glob("api2-devdock-*/main.py"):
        py_compile.compile(str(example), doraise=True)
