import os
import random
import re
import string

from click import style

from .compat import text_type
from .excs import BadUsage


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


def match_step(config, step):
    if step in config.steps:
        return step
    step_matches = match_prefix(config.steps, step)
    if not step_matches:
        raise BadUsage(
            '"{step}" is not a known step (try one of {steps})'.format(
                step=step,
                steps=', '.join(style(t, bold=True) for t in sorted(config.steps))
            ))
    if len(step_matches) > 1:
        raise BadUsage(
            '"{step}" is ambiguous.\nIt matches {matches}.\nKnown steps are {steps}.'.format(
                step=step,
                matches=', '.join(style(t, bold=True) for t in sorted(step_matches)),
                steps=', '.join(style(t, bold=True) for t in sorted(config.steps)),
            ))
    return step_matches[0]
