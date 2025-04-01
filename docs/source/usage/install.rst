Installing the application
==========================


Installing the project (for developers)
---------------------------------------

Start by downloading the project code from the `GitHub repo <https://github.com/mtanti/nomocrat-project>`_.

Inside the project directory, run ``create_venv`` (available as batch or bash script) using a `conda <https://www.anaconda.com/download>`_ command line in order to create a conda virtual environment (in a directory called ``venv``).
This conda virtual environment will contain all the required packages for ``nomocrat_project`` together with the ``nomocrat_project`` project itself.

Following this, install the development packages as well by running

.. code-block::

    pip install -r requirements_dev.txt

You can now run ``check_all`` (available as batch or bash script) to run tests on the project code as well as compile the documentation.
You can also run ``build`` (available as batch or bash script) to distribute the package to PyPI.
