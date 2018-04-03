import json
import os

import pytest
from more_itertools import first

from valohai_local_run.cli import cli
from valohai_local_run.consts import EXECUTION_METADATA_JSON_NAME, STDOUT_LOG_NAME


def test_valohai_local_run(tmpdir, capsys):
    code_dir = tmpdir.mkdir('code')
    inputs_dir = tmpdir.mkdir('inputs')
    outputs_dir = tmpdir.mkdir('outputs')
    code_dir.join('valohai.yaml').write('''
- step:
    name: magical super step
    image: busybox
    command: "ls -laR $VH_INPUTS_DIR; printenv > $VH_OUTPUTS_DIR/proof.txt"
    inputs:
      - name: foo
    parameters:
      - name: inty
        type: integer
        default: -7
      - name: floaty
        type: float
        default: 8.2
''')

    inputs_dir.join('foo-input.txt').write('hello hello hello')

    with pytest.raises(SystemExit) as ei:
        cli([
            '--directory', str(code_dir),
            '--foo=%s/foo-input.txt' % str(inputs_dir),
            '--output-root=%s' % str(outputs_dir),
            '--docker-add-args=--env toto=africa',
            '--floaty=17.3',
            'magic',
        ])

    assert ei.value.code == 0

    out, err = capsys.readouterr()

    # Find the execution ID by looking at the hopefully only directory in the base path
    output_dir_basename = first(os.listdir(str(outputs_dir)))
    # Ensure it was printed for the user too
    assert output_dir_basename in out

    # Find our output files...
    output_dir = os.path.join(str(outputs_dir), output_dir_basename)
    assert os.path.isdir(output_dir)

    # Check outputs get saved correctly
    with open(os.path.join(output_dir, 'proof.txt')) as proof_fp:
        assert 'toto=africa' in proof_fp.read()

    # Check metadata gets saved correctly
    with open(os.path.join(output_dir, EXECUTION_METADATA_JSON_NAME)) as meta_fp:
        meta = json.load(meta_fp)
        assert meta['parameters'] == {
            'floaty': 17.3,
            'inty': -7,
        }

    # Check stdout gets saved correctly
    with open(os.path.join(output_dir, STDOUT_LOG_NAME)) as out_fp:
        assert 'foo-input.txt' in out_fp.read()
