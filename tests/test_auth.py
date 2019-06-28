import auth
import pytest
import os

def test_auth_env_exists():
    fname = join(dirname(__file__),'.auth_env')
    is_file=os.path.isfile(fname)

    assert is_file is True

