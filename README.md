# hepfile

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mattbellis/hepfile/HEAD?urlpath=lab/tree/docs/example_nb)

[![DOI](https://zenodo.org/badge/91502190.svg)](https://zenodo.org/badge/latestdoi/91502190)

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]
[![Gitter][gitter-badge]][gitter-link]




[actions-badge]:            https://github.com/mattbellis/hepfile/workflows/CI/badge.svg
[actions-link]:             https://github.com/mattbellis/hepfile/actions
[black-badge]:              https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]:               https://github.com/psf/black
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/hepfile
[conda-link]:               https://github.com/conda-forge/hepfile-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/mattbellis/hepfile/discussions
[gitter-badge]:             https://badges.gitter.im/https://github.com/mattbellis/hepfile/community.svg
[gitter-link]:              https://gitter.im/https://github.com/mattbellis/hepfile/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
[pypi-link]:                https://pypi.org/project/hepfile/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/hepfile
[pypi-version]:             https://badge.fury.io/py/hepfile.svg
[rtd-badge]:                https://readthedocs.org/projects/hepfile/badge/?version=latest
[rtd-link]:                 https://hepfile.readthedocs.io/en/latest/?badge=latest
[sk-badge]:                 https://scikit-hep.org/assets/images/Scikit--HEP-Project-blue.svg

For local builds for testing. 
```
/home/bellis/.local/bin/flit install
```

or 

```
pip install -e .
```

Install the following packages using `pip`:

```
flit
autodocs # for sphinx
```

Then, run the following commands to setup the pre-commit git hook
to automatically run tests before committing!
```
chmod a+x pre-commit-tests.sh
ln -s ../../pre-commit-tests.sh .git/hooks/pre-commit
```
