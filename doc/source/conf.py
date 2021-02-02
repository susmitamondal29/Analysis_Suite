# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath('..'))
sys.setrecursionlimit(1500)

ana_base = Path("../analysis_suite")
actual_base = Path("../..")
module_dirs = [i for i in actual_base.iterdir() if i.is_dir() and (i/"python").is_dir()]

if not ana_base.is_dir():
    os.mkdir(ana_base)
    module_dirs = [i for i in actual_base.iterdir() if i.is_dir() and (i/"python").is_dir()]
    for module in module_dirs:
        os.symlink(module.resolve()/"python", ana_base/module.name)

for module in module_dirs:
    sys.path.insert(0, (ana_base/module.name).resolve().as_posix())
    

autoclass_content = 'both'
# -- Project information -----------------------------------------------------

project = 'Analysis Suite'
copyright = '2021, Dylan Teague'
author = 'Dylan Teague'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
       'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinxawesome_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

html_css_files = [
    'style.css',
]


