import argparse
import os
from collections import defaultdict
from io import StringIO
from subprocess import check_output

import valohai_yaml

from valohai_local_run.consts import DEFAULT_OUTPUT_ROOT
from valohai_local_run.executor import LocalExecutor
from valohai_local_run.termui import style
from valohai_local_run.utils import match_prefix


def get_argument_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('step')
    ap.add_argument('--commit', '-c', default=None, metavar='SHA',
                    help='The commit to use. Defaults to the current HEAD.')
    ap.add_argument('--environment', '-e', default=None, help='Ignored.')
    ap.add_argument('--image', default=None, help='Override the Docker image specified in the step')
    ap.add_argument('--adhoc', '-a', action='store_true', help='Run as an ad-hoc execution')
    ap.add_argument('--watch', '-w', action='store_true', help='Ignored. Local runs are always watched.')
    ap.add_argument('--project-id', '-p', default=None, help='Project ID.')
    ap.add_argument('--output-root', default=DEFAULT_OUTPUT_ROOT, help='Output root')
    return ap


def add_step_arguments(ap, step):
    for parameter in step.parameters.values():
        ap.add_argument(
            '--%s' % parameter.name.replace('_', '-'),
            dest=':parameters:%s' % parameter.name,
            required=(parameter.default is None and not parameter.optional),
            default=parameter.default,
            help=parameter.description,
        )
    for input in step.inputs.values():
        ap.add_argument(
            '--%s' % input.name.replace('_', '-'),
            dest=':inputs:%s' % input.name,
            required=(input.default is None and not input.optional),
            default=input.default,
            metavar='URL',
            help='Input "%s"' % input.name,
        )


def match_step(config, step):
    if step in config.steps:
        return step
    step_matches = match_prefix(config.steps, step)
    if not step_matches:
        raise ValueError(
            '"{step}" is not a known step (try one of {steps})'.format(
                step=step,
                steps=', '.join(style(t, bold=True) for t in sorted(config.steps))
            ))
    if len(step_matches) > 1:
        raise ValueError(
            '"{step}" is ambiguous.\nIt matches {matches}.\nKnown steps are {steps}.'.format(
                step=step,
                matches=', '.join(style(t, bold=True) for t in sorted(step_matches)),
                steps=', '.join(style(t, bold=True) for t in sorted(config.steps)),
            ))
    return step_matches[0]


def cli(argv=None):
    directory = os.getcwd()
    ap = get_argument_parser()
    args, rest_argv = ap.parse_known_args(argv)

    if args.adhoc:
        raise NotImplementedError('Local executions with ad-hoc commits are not supported yet.')

    if not args.commit:
        args.commit = check_output(['git', 'rev-parse', 'HEAD'], cwd=directory).strip().decode()
    else:
        args.commit = check_output(['git', 'rev-parse', '--verify', args.commit], cwd=directory).decode().strip()

    config_data = check_output(['git', 'show', '{}:valohai.yaml'.format(args.commit)], cwd=directory).decode()
    config = valohai_yaml.parse(StringIO(config_data))
    step = config.steps[match_step(config, args.step)]

    add_step_arguments(ap, step)

    opt_args = ap.parse_args(argv)
    dicts = defaultdict(dict)
    for name, value in vars(opt_args).items():
        if name.startswith(':'):
            _, dict_name, name = name.split(':', 2)
            dicts[dict_name][name] = value

    executor = LocalExecutor(
        commit=args.commit,
        directory=directory,
        image=args.image,
        inputs=dicts['inputs'],
        output_root=args.output_root,
        parameters=dicts['parameters'],
        project_id=args.project_id,
        step=step,
    )
    executor.execute(verbose=True)
