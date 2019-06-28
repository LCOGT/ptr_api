import ptr_api.auth
import pytest
from os.path import join, dirname, isfile


def test_auth_env_exists():
    fname = join(dirname(__file__),'../ptr_api/.auth_env')
    is_file = isfile(fname)

    assert is_file is True


