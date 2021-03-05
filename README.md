perma-mirror
============

This program watches an SQS queue and downloads newly-created S3
objects. It is intended to mirror WARCs created by
[perma.cc](https://perma.cc/).

Usage
-----

For regular use, start a virtual environment and install the
requirements, something like this:

    python3 -m venv env
	source env/bin/activate
	pip install -r requirements.txt

Now you can run

    python poll_for_warcs.py --help

For development, [install
Poetry](https://python-poetry.org/docs/#installation), run `source
$HOME/.poetry/env` and install requirements like this:

    poetry install

Now you can run

    poetry run python poll_for_warcs.py --help

If you update any packages, run `poetry export > requirements.txt` to
keep it in sync with `poetry.lock`.

(A stretch goal will be to use `poetry` to publish a package to PyPI,
so that we don't have to install requirements "by hand" in
production.)
