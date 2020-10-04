.. Simulation FastAPI documentation master file, created by
   sphinx-quickstart on Mon Sep 28 19:08:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _topics-index:

===========================================
PHYS Simulation API |version| documentation
===========================================

Using PHYS Simulation API you can request simulations of some physical or 
mathematical systems such as the `Harmonic Oscillator`_ or the
`Chen-Lee Attractor`_ –and soon many others, stay tuned!

.. _Harmonic Oscillator: https://en.wikipedia.org/wiki/Harmonic_oscillator
.. _Chen-Lee Attractor: https://doi.org/10.1016/j.chaos.2003.12.034 

History
=======

PHYS Simulation API started as a way of learning to develop a web application.
We believe that the best way of learning is by doing. This way, we chose
a topic that drives us (yes, physics and mathematics!) and started learning by
writting code! Of course, we had to read a lot and fail a lot as well, but
we managed to develop our very first web application and we are proud of it, as
impefect as it may be.

In the future we want to add as many features as we can, so far that it enriches
the user experience.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   start/overview
   start/examples
   start/frontend

==============
For Developers
==============

This API is built on top of `FastAPI`_. If you want to contribute to this
project, you may find `their docs`_ very useful.

In this section you can find all the source code docuentation. If you have a
question on how some function, class or method works, maybe it's answered here.
If not, do not hesitate to `contact us`_.

.. _FastAPI: https://github.com/tiangolo/fastapi
.. _their docs: https://fastapi.tiangolo.com/
.. _contact us: mailto:jeaz.git@gmail.com

The Code
========

.. toctree::
   :caption: THE CODE
   :hidden:

   code_docs/simulation_API
   code_docs/new_simulation

:mod:`simulation_API`
   Initialization of web application.

   :mod:`simulation_API.controller`
      The core package of our API. Here you can find the main app, schemas and
      background tasks.

   :mod:`simulation_API.model`
      Database-related package.

   :mod:`simulation_API.simulation`
      Simulation-related package. Here you can find all the programs we use to
      simulate the available systems.

   :mod:`simulation_API.config`
      Configuration module. Some very basic configurations of our web application.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


A Special Aknowledgement
------------------------

To Camilo Hincapié who guided me in this process.