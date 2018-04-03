valohai-local-run
=================

![CircleCI](https://img.shields.io/circleci/project/github/valohai/valohai-local-run.svg)
![Codecov](https://img.shields.io/codecov/c/github/valohai/valohai-local-run.svg)
![PyPI](https://img.shields.io/pypi/v/valohai-local-run.svg)
![MIT License](https://img.shields.io/github/license/valohai/valohai-local-run.svg)


This utility allows you to run experiments designed for the
[Valohai IaaS Machine Learning Platform][valohai] on local Linux hardware.

Unlike the platform, this tool does not offer any reproducibility,
bookkeeping and collaboration features. It is meant for "pre-flight" testing
of code packaged for Valohai, and local runs in environments not reachable
via the Internet.

Requirements
------------

* Python 3.4+ with Pip
* Git
* Docker (configured to be available for the user running `valohai-local-run`)

Installation
------------

`valohai-local-run` is available on the Python [PyPI][pypi] package registry.
To install the latest released version, simply run `pip install valohai-local-run`
(optionally with the `--user` flag to allow for non-root installs).  You may
also use a Python virtualenv to install in.

You can also install a development version by cloning the repository and running 
`pip install -e .` in the working copy directory.

Usage
-----

The syntax of `valohai-local-run` mostly mirrors that of the [Valohai CLI][cli]'s
`exec run` command.

Assuming the `valohai-local-run` command is available within your shell's PATH
(by way of installation or virtualenv activation, or otherwise – if you installed
with `pip --user`, it may be in `~/.local/bin`), you can simply run

```bash
$ valohai-local-run step-name --help
``` 

where `step-name` is the name of a step, as described in the `valohai.yaml` file,
to see the syntax for the parameters and inputs, e.g. for the [Tensorflow example][tfe]:

```
parameters for "Train model":
  --max-steps INTEGER   Number of steps to run the trainer
  --learning-rate FLOAT
                        Initial learning rate
  --dropout FLOAT       Keep probability for training dropout

inputs for "Train model":
  --training-set-images URL
                        Input "training-set-images"
  --training-set-labels URL
                        Input "training-set-labels"
  --test-set-images URL
                        Input "test-set-images"
  --test-set-labels URL
                        Input "test-set-labels"
```

Other arguments supported by `vh exec run` are also available; see the full `--help` output.

The metadata, logs and output files resulting from a run are saved into a timestamped directory.
By default the directory is created within `valohai-local-outputs` in the working directory.
This output root path may be changed with the `--output-root` argument.

### Input syntax

Inputs may be HTTP/HTTPS URLs if the `requests` package is available.  
Paths to directories and files are always supported.
When all paths are files, multiple repetitions of a single input argument is accepted, and
the files are mounted with their original names within the `/valohai/inputs/input-name` virtual
directory.

When a path is a directory, that directory is assumed to be the entirety of that input,
i.e. the directory is mounted as `/valohai/inputs/input-name`.  All inputs are mounted read-only.

Running with GPU support
------------------------

There is tentative support for running on local GPU devices.
This relies on the [`nvidia-docker`][nd] package; please follow its installation
instructions first.

Once `nvidia-docker` is installed, you can direct `valohai-local-run` to use it with
either the `--docker-command` or `--docker-add-args` arguments, as follows:

* If you are using `nvidia-docker` 1.x, add `--docker-command=nvidia-docker`.
* If you are using `nvidia-docker` 2.x, add `--docker-add-args=--runtime=nvidia`.

[valohai]: https://valohai.com/?utm_source=valohai-local-run-readme
[pypi]: https://pypi.org/project/valohai-local-run/
[cli]: https://github.com/valohai/valohai-cli/
[tfe]: https://github.com/valohai/tensorflow-example/
[nd]: https://github.com/NVIDIA/nvidia-docker
