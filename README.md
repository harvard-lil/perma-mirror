perma-mirror
============

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

Now you can run

    poll-for-warcs --help

For development, [install
Poetry](https://python-poetry.org/docs/#installation), run `source
$HOME/.poetry/env`, then install this package and its requirements
like this:

    poetry install

Now you can run

    poetry run poll-for-warcs --help
