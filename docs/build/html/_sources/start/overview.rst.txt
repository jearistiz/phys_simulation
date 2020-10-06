.. _start-overview:

========
Overview
========

In PHYS Simulation API you can request –via HTTP POST method– a simulation from
a list of available simulations. Here we will show you the schemas you need to
appropiately request your simulation. In :ref:`Examples <start-examples>` you
will see how this works in the real life.

Request a simulation
====================

The simulation requests are made in route ``/api/simulate/{sim_system}``,
where ``sim_system`` is one of the members of
:py:class:`~simulation_API.controller.schemas.SimSystem`.

The body of the request must abide by the following schema

.. jsonschema:: ../json/_SimRequest.json

The body of the HTML response will have the following schema

.. _simidresponse:

.. jsonschema:: ../json/_SimIdResponse.json

Request Simulation Status
=========================

The response of the request simulation (:ref:`SimIdResponse <simidresponse>`)
contains a simulation ID, ``sim_id``. In order to know the simulation status you
just need to make an HTTP request via GET with empty body in route
``/api/request/status/{sim_id}``.

.. note::

   The route will be availble just after the simulation is finished. If you do
   not receive a successful response and you are sure about the ``sim_id`` you
   provided in the API route, the simulation may still be in course.

The schema of the response will be the following

.. _simstatus:

.. jsonschema:: ../json/_SimStatus.json

Request Results
===============

If ``success=True`` in :ref:`SimStatus <simstatus>`, you can

1. `Directly download your results`
   
   a. Download pickle file with all the simulation results as returned by
      `scipy.integrate.solve_ivp`_. You can do this via GET with empty body
      in route ``/api/results/{sim_id}/pickle``.
   b. Download your simulation's automatically generated plots. You can do this
      via GET with empty body in route
      ``/api/results/{sim_id}/plot?value={plot_query_value}``, where
      ``plot_query_value`` is one of the items in ``plot_query_values`` in the
      simulation status, :ref:`SimStatus <simstatus>`.

2. `See your results online`. You can do this via GET in route
   ``/results/{sim_system}/{sim_id}``. In the rendered HTML file, you have the
   option to download both the generated plots and the pickle file mentioned in
   the last item.

.. _scipy.integrate.solve_ivp: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
