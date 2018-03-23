import os
import random
import re
import string

from valohai_local_run.compat import text_type


def get_random_string(length=12, keyspace=(string.ascii_letters + string.digits)):
    return ''.join(random.choice(keyspace) for x in range(length))


def ensure_makedirs(path, mode=0o744):
    # http://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-python
    original_umask = os.umask(0)
    try:
        # only newly create directories get the defined mode
        os.makedirs(path, mode=mode, exist_ok=True)
        # ensure that the last directory has the right mode if it exists
        os.chmod(path, mode=mode)
    finally:
        os.umask(original_umask)


def match_prefix(choices, value):
    value_re = re.compile('^' + re.escape(value), re.I)
    choices = [choice for choice in choices if value_re.match(text_type(choice))]
    return choices
