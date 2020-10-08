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

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = 'PHYS Simulation API'
copyright = '2020, Juan E. Aristizabal'
author = 'Juan E. Aristizabal'

# The full version, including alpha/beta/rc tags
version = '1.0'
release = '1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.viewcode',
    #'sphinx.ext.linkcode',  # Shows code in github, but showing exact codeblock is difficult to configure. See numpy's documentation conf.py, for example.
    #'hoverxref.extension',
    'sphinx.ext.autodoc',
    'sphinx-jsonschema',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
]

# Linkcode extension configuration function - Very complicated to link to
# codeblock. Much easier: use  viewcode.
# def linkcode_resolve(domain, info):
#     if domain != 'py':
#         return None
#     if not info['module']:
#         return None
#     filename = info['module'].replace('.', '/')
#     return "https://github.com/jearistiz/simulation-api/blob/master/%s.py" % filename

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

autodoc_default_options = {
    'members': True,
    'private-members': # from controller.tasks
                       '_api_simulation_request, '
                       '_create_pickle_path_disk, '
                       '_create_plot_path_disk, '
                       '_pickle, '
                       '_plot_solution, '
                       '_run_simulation, '
                       '_sim_form_to_sim_request, '
                       '_check_chen_lee_params, '
                       # from model.models
                       '_create_user, '
                       '_get_username, '
                       '_create_simulation, '
                       '_get_simulation, '
                       '_get_all_simulations, '
                       '_create_plot_query_values, '
                       '_get_plot_query_values, '
                       '_create_parameters, '
                       '_get_parameters',
    'special-members': '__init__',
    'inherited-members': False,
    'show-inheritance': False,
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme =  "sphinx_rtd_theme"  # 'classic' # 'sphinx_material'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = True

# favicon
html_favicon = '../../simulation_API/static/img/favicon.ico'

# Background color for code blocks 
codebgcolor = '#F0FFFF' # Did not work wih read the docs theme

# Some latex configurations, therea re many other options...
# If you want internal links in your pdf, run twise 'make latexpdf'.
latex_elements = {
     'papersize': 'a4paper,landscape',
}

# sphinx-jsonschema configurations
jsonschema_options = {
    "lift_title": True,
}

# hoverxref configurations (taken from conf.py from hoverxref documentation source code)
# hoverxref_tooltip_maxwidth = 650
# hoverxref_auto_ref = True
# hoverxref_roles = [
#     'confval',
# ]

# hoverxref_role_types = {
#     'hoverxref': 'tooltip',
#     'ref': 'modal',
#     'confval': 'tooltip',
#     'mod': 'modal',
#     'class': 'modal',
# }
# hoverxref_domains = [
#     'py',
# ]
# hoverxref_sphinxtabs = True
# hoverxref_mathjax = True