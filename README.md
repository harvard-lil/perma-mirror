perma-mirror
============

This program watches an SQS queue and downloads newly-created S3
objects. It is intended to mirror WARCs created by
[perma.cc](https://perma.cc/).

Usage
-----

At the moment, start a virtual environment and install the
requirements, something like this:

    python3 -m venv env
	source env/bin/activate
	pip install -r requirements.txt

Now you can run

    python poll_for_warcs.py --help

Alternatively, [install
Poetry](https://python-poetry.org/docs/#installation), run `source
$HOME/.poetry/env` and install requirements like this:

    poetry install

Now you can run

    poetry run python poll_for_warcs.py --help

(The `poetry` mechanism is preferable, but the traditional
`requirements.txt` will remain here until deployment using `poetry` is
set up.)
