# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Warning: do not change the path here. To use autodoc, you need to install the
# package first.

from typing import List


import sys
import os
sys.path.append(os.path.abspath(os.pardir))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))


# -- Project information -----------------------------------------------------

project = "hepfile"
copyright = "2021, Matt Bellis"
author = "Matt Bellis"
version = "0.2.0"
release = "0.2.0"

# The master toctree document.
master_doc = 'index'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "**.ipynb_checkpoints", "Thumbs.db", ".DS_Store", ".env"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = "sphinx_book_theme"
html_theme = "sphinx_rtd_theme"

html_title = f"hepfile {version}"
#html_title = f"hepfile 0.09"

html_baseurl = "https://hepfile.readthedocs.io/en/latest/"

'''
# For sphinx-book-theme
html_theme_options = {
    "home_page_in_toc": True,
    "repository_url": "https://github.com/mattbellis/hepfile",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
}
'''

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path: List[str] = []
