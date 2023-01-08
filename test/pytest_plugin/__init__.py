import sys

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None and '--forked' in args:
        args.remove('--forked')
