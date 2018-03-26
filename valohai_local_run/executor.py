import datetime
import json
import os
import subprocess
import tempfile
import time
from itertools import chain

from click import echo, secho, style

from .consts import volume_mount_targets
from .inputs import prepare_inputs
from .utils import ensure_makedirs, get_random_string


def build_volume_params(volumes):
    volume_params = []
    for volume_desc in volumes:
        volume_param = '%s:%s' % (os.path.realpath(volume_desc['source']), volume_desc['destination'])
        if volume_desc.get('readonly'):
            volume_param += ':ro'
        volume_params.extend(['-v', volume_param])

    return volume_params


def build_env_params(env_vars):
    env_params = []
    for key, value in sorted(env_vars.items()):
        env_params.extend(['-e', '%s=%s' % (key, value)])
    return env_params


class LocalExecutor:
    def __init__(
        self,
        project_id,
        directory,
        commit,
        step,
        inputs,
        parameters,
        output_root,
        command=None,
        image=None,
        docker_command='docker',
    ):
        self.project_id = project_id
        self.directory = directory
        self.commit = commit
        self.step = step
        self.inputs = inputs
        self.parameters = parameters
        self.command = (command or self.step.command)
        self.interpolated_command = (
            self.step.build_command(self.parameters, command=(self.command or self.step.command))
        )
        self.image = (image or self.step.image)
        self.output_root = output_root
        self.docker_command = docker_command
        self.execution_id = '{}-{}'.format(time.strftime('%Y%m%d-%H%M%S'), get_random_string(5))
        self.repository_dir = tempfile.mkdtemp(prefix='valohai-code-' + self.execution_id)
        self.output_dir = os.path.join(output_root, self.execution_id)
        ensure_makedirs(self.output_dir, 0o770)

    def prepare(self, verbose):
        input_volumes = list(prepare_inputs(self.inputs, verbose=verbose))
        self.clone_repo()
        self.write_metadata_file()
        return self.build_docker_command(input_volumes)

    def execute(self, verbose=False):
        command = self.prepare(verbose=verbose)
        if verbose:
            self.print_report()
        subprocess.call(command)

    def print_report(self):
        echo('-> Using commit {}, step "{}"'.format(
            style(self.commit, bold=True),
            style(self.step.name, bold=True),
        ))
        echo('-> Using image {}'.format(style(self.image, bold=True)))
        echo('-> Using command {}'.format(style(self.command, bold=True)))
        echo('=> Outputs will be written to {}'.format(style(self.output_dir, bold=True)))
        secho('=== Starting execution! ===', bold=True, fg='green')

    def write_metadata_file(self):
        with open(os.path.join(self.output_dir, 'valohai-execution-metadata.json'), 'w') as outf:
            json.dump(self.get_metadata_blob(), outf, indent=2, sort_keys=True, ensure_ascii=True)

    def get_metadata_blob(self):
        return {
            'command': self.command,
            'commit': self.commit,
            'image': self.image,
            'inputs': self.inputs,
            'interpolated_command': self.interpolated_command,
            'parameters': self.parameters,
            'project': self.project_id,
            'step': self.step.name,
            'time': datetime.datetime.now().isoformat(),
        }

    def clone_repo(self):
        # Clone the desired commit into a temporary directory.
        source_git_dir = self.directory
        assert os.path.isdir(source_git_dir)
        dest_git_dir = self.repository_dir
        subprocess.check_call(
            ['git', 'clone', '--shared', '--no-checkout', '--', source_git_dir, dest_git_dir],
            stderr=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ['git', 'checkout', self.commit],
            cwd=dest_git_dir,
            stderr=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ['git', 'submodule', 'update', '--init'],
            cwd=dest_git_dir,
        )

    def build_docker_command(self, input_volumes=()):
        command = ' && '.join(self.interpolated_command)

        docker_command = [
            '/usr/bin/env',
            self.docker_command,
            'run',
            '--entrypoint=',
            '--workdir=%s' % volume_mount_targets['repository'],
            '-it',
            '--name', 'valohai-local-%s' % self.execution_id,
        ]
        env_vars = {
            'PYTHONUNBUFFERED': '1',
            'VH_REPOSITORY_DIR': volume_mount_targets['repository'],
            'VH_INPUTS_DIR': volume_mount_targets['inputs'],
            'VH_OUTPUTS_DIR': volume_mount_targets['outputs'],
        }
        docker_command.extend(build_env_params(env_vars))
        docker_command.extend(self.build_volume_params(input_volumes))
        docker_command.extend([
            self.image,
            '/bin/sh',  # TODO: This could use `/bin/bash` too if available
            '-c',
            command,
        ])
        return docker_command

    def build_volume_params(self, input_volumes):
        volumes = [
            {'source': self.repository_dir, 'destination': volume_mount_targets['repository']},
            {'source': self.output_dir, 'destination': volume_mount_targets['outputs']},
        ]
        return build_volume_params(chain(volumes, input_volumes))
