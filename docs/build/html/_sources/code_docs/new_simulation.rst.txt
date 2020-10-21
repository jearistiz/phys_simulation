.. _code-new-simulation:

====================
Add a new simulation
====================

Keep in mind that the systems we can add to our API are those that can be
integrated by ``scipy.integrate.solve_ivp``. Those are basically first order
coupled differential equations i.e. systems of the form

.. math::
   \frac{d\mathbf{y}}{dt} = \mathbf{f}(\mathbf{y}, t).

If you want to add a new simulation to this API just follow the steps described
below.

1. Add the simulation to :py:mod:`~simulation_api.simulation.simulations` module
================================================================================

1. Add a relevant class to :py:mod:`~simulation_api.simulation.simulations`.
   This class will define the relevant parameters used in the simulation as well
   as its dynamic equations. It must inherit
   :py:class:`~simulation_api.simulation.simulations.Simulation`
   and must have the same structure as
   :py:class:`~simulation_api.simulation.simulations.HarmonicOsc1D` and
   :py:class:`~simulation_api.simulation.simulations.ChenLeeAttractor`. Don't
   forget to test your simulation by playing around in
   :py:mod:`~simulation_api.simulation.demo_run_simulation`.
2. Don't forget to add the attribute
   :py:attr:`~simulation_api.simulation.simulations.Simulation.system` to your
   class. The value of this attribute must be the name of the system separated
   by dashes. Use only alphanumerical characters and dashes.
3. Add the relevant simulation class you just created to the ``dict``
   :py:data:`~simulation_api.simulation.simulations.Simulations`. This will tell
   the API that the simulation exists and it is available.

.. _new-simulation-schemas:

2. Add relevant schemas and models to :py:mod:`~simulation_api.controller.schemas`
==================================================================================

Follow the steps mentioned below –some of them may not make sense at first
glance, but until you write the code.

1. Add the :py:attr:`~simulation_api.simulation.simulations.Simulation.system`
   attribute value of the recently created class to
   :py:class:`~simulation_api.controller.schemas.SimSystem`.
2. Create a class that inherits :py:class:`~simulation_api.controller.schemas.SimForm`.
   It must be similar to :py:class:`~simulation_api.controller.schemas.HOSimForm`
   and :py:class:`~simulation_api.controller.schemas.ChenLeeSimForm`. This class
   will be used to check the simulation information provided in frontend.
3. Add a relevant item –related to the class created in the last numeral– to the
   ``dict`` :py:data:`~simulation_api.controller.schemas.SimFormDict`. This will
   map the name of the system to its simulation form model.
4. Add a new class similar to :py:class:`~simulation_api.controller.schemas.HOParams`
   and :py:class:`~simulation_api.controller.schemas.ChenLeeParams`. The names
   of the attributes must match the names of the parameters defined in the
   relevant simulation class, created in the first numeral of this list.
5. Add an appropiate item to the ``dict``
   :py:data:`~simulation_api.controller.schemas.SimSystem_to_SimParams`.
6. Create an appropiate ``dict`` similar to
   :py:data:`~simulation_api.controller.schemas.params_mapping_HO` and
   :py:data:`~simulation_api.controller.schemas.params_mapping_ChenLee`.
7. Add an appropiate item to the dict
   :py:data:`~simulation_api.controller.schemas.system_to_params_dict`.
8. Create a new class similar to
   :py:class:`~simulation_api.controller.schemas.PlotQueryValues_HO` and
   :py:class:`~simulation_api.controller.schemas.PlotQueryValues_ChenLee`.
9. Add an appropiate item to :py:data:`~simulation_api.controller.schemas.PlotQueryValues`.

If you do not understand some of the steps above or how to implement them, refer
to :ref:`the documentaton <code-API-package>` of the relevant classes or schemas
for the already available systems –Chen-Lee Attractor or Harmonic Oscillator–,
it may enlighten you.
   
3. Add relevant plots to :py:func:`~simulation_api.controller.tasks._plot_solution`
===================================================================================

Here you can add two or three intersting plots related to the simulation you
just added and tested. The code that generates the plots must be placed in
:py:func:`simulation_api.controller.tasks._plot_solution`.

A few things to take into account:

1. We use matplotlib, but we use the class ``Figure`` directly, we do not use
   pyplot. This is related to some problems that may arise with the pyplot
   package and the web applocation backend, as mentioned in
   `matplotlib's documentation`_.
2. Note that the plots related to the simulations are defined in an ``if`` or
   ``elif`` block each one. Add a new block for the simulation you want to add.
3. The first two lines of code that generate each plot related to the recently
   created simulation must look something like::
      
      plot_query_value = PlotQueryValues_HO.phase.value
      plot_query_values.append(plot_query_value)

   For each generated plot, we define a ``plot_query_value`` that comes directly
   from the class defined in item number 8 of the
   :ref:`last section <new-simulation-schemas>`. In the example given above, 
   the class was named ``PlotQueryValues_HO``, the attribute related to the
   ``plot_query_value`` of the relevant plot was named ``coord`` and the value
   of the latter is accessed by using ``.value``.
   Each ``plot_query_value`` is appended to the list ``plot_query_values``,
   which is the return value of :py:func:`~simulation_api.controller.tasks._plot_solution`.
   This item is very important, since the values we define here are used to name
   the plots as well as to look them up.
4. Finally, the last line of code that generates each plot must be::
      
      fig.savefig(_create_plot_path_disk(plots_basename, plot_query_value))
   
   This will ensure that the name of the plot has always the same format

.. _matplotlib's documentation: https://matplotlib.org/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server

4. Add relevant form entries in frontend
========================================

Modify appropiately the template ``simulation_api/templates/request-simulation.html``.
This template is the one that asks for the simulation parameters in the frontend.

Some things to take into account:

1. Note that each system has its own ``if`` or ``elif`` block. Stick to this
   convention and add a new block related to the new simulation (the new system).
2. In the ``if`` block mentioned above there are only two main things the form
   should ask for: initial conditions and parameters of simulation.
3. For the initial conditions the value of the HTML attribute ``name`` should start
   with the string ``"ini"`` followed by the index in the initial condition
   array defined in your simulation class attribute ``ini_cndtn``.
   For example, for the harmonic oscillator the convention of initial condition
   is :math:`\texttt{ini_cndtn} = [q_0, p_0]`. So, :math:`q_0` will be associated
   with ``name="ini0"`` and :math:`p_0` with ``name="ini1"``.
4. Analogous to the initial condition convention mentioned in the last
   item, you must choose an arbitrary convention for the names of the parameters
   of each specific system but you should stick to this convention when defining
   the models and schemas associated to the parameters and mentioned in
   :ref:`the previous to last section <new-simulation-schemas>`.
   Specifically, you should stick to the convention you define here and follow
   it in item number 6 of the previous to last section. For example, in the
   Harmonic Oscillator we chose the convention of associating the parameter
   ``m`` with the HTML attribute ``name="param0"`` and ``k`` with
   ``name="param1"``. You can check that
   ``simulation_api/templates/request-simulation.html`` as well as
   :py:data:`~simulation_api.controller.schemas.params_mapping_HO` follow this
   convention.

5. Modify ``results.html`` template to show results
===================================================

Finally, we need to add a relevant ``elif`` block to the template
``simulation_api/templates/results.html``. This template should show the
generated plots, give the option to download them with a button and
give the option to download the pickle file as well.