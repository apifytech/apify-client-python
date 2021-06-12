# Apify API client for Python

This is an official client for the [Apify API](https://www.apify.com/docs/api/v2).
It's still a work in progress, so please don't use it yet in production environments!

## Installation

Requires Python 3.7+

You can install the client from its [PyPI listing](https://pypi.org/project/apify-client).
To do that, simply run `pip install apify-client` in your terminal.

## Usage

For usage instructions, check the documentation on [Apify Docs](https://docs.apify.com/apify-client-python) or in [`docs/docs.md`](docs/docs.md).

## Development

### Environment

For local development, it is required to have Python 3.7 installed.

It is recommended to set up a virtual environment while developing this package to isolate your development environment,
however, due to the many varied ways Python can be installed and virtual environments can be set up,
this is left up to the developers to do themselves.

One recommended way is with the builtin `venv` module:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

To improve on the experience, you can use [pyenv](https://github.com/pyenv/pyenv) to have an environment with a pinned Python version,
and [direnv](https://github.com/direnv/direnv) to automatically activate/deactivate the environment when you enter/exit the project folder.

### Dependencies

To install this package and its development dependencies, run `pip install -e '.[dev]'`

### Formatting

We use `autopep8` and `isort` to automatically format the code to a common format. To run the formatting, just run `./format.sh`.

### Linting and Testing

We use `flake8` for linting, `mypy` for type checking and `pytest` for unit testing. To run these tools, just run `./lint_and_test.sh`.

### Documentation

We use the [Google docstring format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for documenting the code.
We document every user-facing class or method, and enforce that using the flake8-docstrings library.

The documentation is then rendered from the docstrings in the code using Sphinx and some heavy post-processing and saved as `docs/docs.md`.
To generate the documentation, just run `./build_docs.sh`.

### Release process

Publishing new versions to [PyPI](https://pypi.org/project/apify-client) happens automatically through GitHub Actions.

On each commit to the `master` branch, a new beta release is published, taking the version number from `src/apify_client/_version.py`
and automatically incrementing the beta version suffix by 1 from the last beta release published to PyPI.

A stable version is published when a new release is created using GitHub Releases, again taking the version number from `src/apify_client/_version.py`. The built package assets are automatically uploaded to the GitHub release.

If there is already a stable version with the same version number as in `src/apify_client/_version.py` published to PyPI, the publish process fails,
so don't forget to update the version number before releasing a new version.
The release process also fails when the released version is not described in `CHANGELOG.md`,
so don't forget to describe the changes in the new version there.
