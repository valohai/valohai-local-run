"""
Termui functions adapted from Click. Click is (c) 2014 by Armin Ronacher, licensed under the BSD license.
"""
import re
import sys
from contextlib import contextmanager

from valohai_local_run.compat import text_type

_ansi_colors = (
    'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'reset',
)
_ansi_reset_all = '\033[0m'
_ansi_re = re.compile('\033\[((?:\d|;)*)([a-zA-Z])')


def strip_ansi(value):
    return _ansi_re.sub('', value)


def isatty(stream):
    try:
        return stream.isatty()
    except Exception:
        return False


def style(
    text, fg=None, bg=None, bold=None, dim=None, underline=None,
    blink=None, reverse=None, reset=True,
):
    bits = []
    if fg:
        try:
            bits.append('\033[%dm' % (_ansi_colors.index(fg) + 30))
        except ValueError:
            raise TypeError('Unknown color %r' % fg)
    if bg:
        try:
            bits.append('\033[%dm' % (_ansi_colors.index(bg) + 40))
        except ValueError:
            raise TypeError('Unknown color %r' % bg)
    if bold is not None:
        bits.append('\033[%dm' % (1 if bold else 22))
    if dim is not None:
        bits.append('\033[%dm' % (2 if dim else 22))
    if underline is not None:
        bits.append('\033[%dm' % (4 if underline else 24))
    if blink is not None:
        bits.append('\033[%dm' % (5 if blink else 25))
    if reverse is not None:
        bits.append('\033[%dm' % (7 if reverse else 27))
    bits.append(text)
    if reset:
        bits.append(_ansi_reset_all)
    return ''.join(bits)


def unstyle(text):
    return strip_ansi(text)


def secho(text, file=None, nl=True, err=False, color=None, **styles):
    return echo(style(text, **styles), file=file, nl=nl, err=err, color=color)


def echo(message=None, file=None, nl=True, err=False, color=True):
    file = file or (sys.stderr if err else sys.stdout)

    if message is not None:
        message = text_type(message)

    if nl:
        message = message or u''
        message += u'\n'

    if message:
        if not (color and isatty(file)):
            message = strip_ansi(message)
        file.write(message)
        file.flush()


def progressbar(object, **kwargs):
    try:
        import click
        return click.progressbar(object, **kwargs)
    except ImportError:
        @contextmanager
        def progressbar(object, *args, **kwargs):
            yield object

        return progressbar
