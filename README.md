perma-mirror
============

[![CircleCI](https://circleci.com/gh/harvard-lil/perma-mirror.svg?style=svg)](https://circleci.com/gh/harvard-lil/perma-mirror)

This program watches an SQS queue and downloads newly-created S3
objects. It is intended to mirror WARCs created by
[perma.cc](https://perma.cc/).

Usage
-----

For regular use, start a virtual environment and install this package
and its requirements, something like this:

    python3 -m venv env
    source env/bin/activate
    pip install git+https://github.com/harvard-lil/perma-mirror#egg=perma-mirror

(At the moment, this code is tested with Python 3.7, and 3.10 is known
not to work.)

Now you can run

    poll-for-warcs --help

For development, [install
Poetry](https://python-poetry.org/docs/#installation), run `source
$HOME/.poetry/env`, and clone this repository. Then, in the repo's
directory, install the package and its requirements like this:

    poetry install

Now you can run

    poetry run poll-for-warcs --help
