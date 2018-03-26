import hashlib
import os
import tempfile

import click

from .utils import ensure_makedirs


def download_url(url, with_progress=True):
    cache_identifier = url
    if '?' in cache_identifier:
        cache_identifier = cache_identifier[:cache_identifier.index('?')]

    _, ext = os.path.splitext(cache_identifier)
    cache_filename = 'download-%s%s' % (
        hashlib.sha1(cache_identifier.encode('utf-8')).hexdigest(),
        ext,
    )

    cache_path = os.path.join(tempfile.gettempdir(), 'valohai-local-run-cache')
    ensure_makedirs(cache_path, 0o770)
    cache_path = os.path.join(cache_path, cache_filename)
    if not os.path.isfile(cache_path):
        try:
            import requests
        except ImportError:
            raise RuntimeError(
                'The `requests` module must be available for download support (attempting to download %s)' % url
            )

        r = requests.get(url, stream=True)
        r.raise_for_status()
        total = (int(r.headers['content-length']) if 'content-length' in r.headers else None)
        byte_iterator = r.iter_content(chunk_size=1048576)

        progress = click.progressbar(byte_iterator, length=total, label=url, width=0)
        progress.is_hidden = (not with_progress)

        with open(cache_path, 'wb') as f, progress:
            for chunk in progress:
                if chunk:  # pragma: no branch
                    f.write(chunk)
    return cache_path
