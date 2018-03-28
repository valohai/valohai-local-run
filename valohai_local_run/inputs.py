import os
import posixpath
from stat import S_ISDIR, S_ISREG

from click import echo, style
from valohai_yaml.utils import listify

from .consts import volume_mount_targets
from .download import download_url


def prepare_inputs(input_dict, verbose=False):
    for input_name, input_specs in input_dict.items():
        input_specs = listify(input_specs)
        multiple_specs = (len(input_specs) > 1)
        for filename in input_specs:
            obj = _prepare_single_input(input_name, filename, multiple_specs)
            if verbose:
                echo('Input {name}: {source} -> {target}'.format(
                    name=style(input_name, bold=True, fg='blue'),
                    source=style(filename, bold=True),
                    target=style(obj['destination'], bold=True),
                ))
            yield obj


def _prepare_single_input(input_name, filename, multiple_specs):
    dest_filename = os.path.basename(filename)
    if filename.startswith('s3:'):
        raise NotImplementedError('S3 inputs are not supported for local runs')

    if filename.startswith('http://') or filename.startswith('https://'):
        filename = download_url(filename, with_progress=True)

    fstat = os.stat(filename)

    if S_ISDIR(fstat.st_mode):  # Bind entire directory
        if multiple_specs:
            raise ValueError((
                '{name} has more than one input file; '
                'with more than one input file, input directories are forbidden.'
            ).format(name=input_name))

        return {
            'source': filename,
            'destination': posixpath.join(
                volume_mount_targets['inputs'],
                input_name,
            ),
            'readonly': True,
        }

    if S_ISREG(fstat.st_mode):  # Bind single file
        return {
            'source': filename,
            'destination': posixpath.join(
                volume_mount_targets['inputs'],
                input_name,
                dest_filename,
            ),
            'readonly': True,
        }

    raise ValueError(
        '{name}: file {filename} is not a regular file or a directory; can\'t use as an input'.format(
            name=input_name,
            filename=filename,
        )
    )
