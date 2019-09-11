import sys
import pytest

def test_python_version():
    if "3.7" in sys.version:
        pass
    else:
        pytest.fail("Python Version : {}".format(sys.version))