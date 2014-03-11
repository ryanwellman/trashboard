import os

TEST_FULL = os.environ.get('REGIONAL_TEST_FULL', 'false')
if TEST_FULL.lower() in ('1', 'true', 'on', 'yes'):
    from .test.full import *
