Installation quickstart
-----------------------

For non-developers, :code:`hepfile` can be installed using :code:`pip`.
`hepfile` includes some optional features that include optional dependencies so there are multiple
different options for installation.

The base package gives you the ability to read and write hepfiles using the more standard "loop & pack"
method and the dictionary tools. This is the "lightest" of the installation options and  is only dependent
on :code:`numpy` and :code:`h5py`. To install the base package use:
::

   python -m pip install hepfile

You can also get the :code:`awkward_tools` which is the hepfile integration with the awkward package. This is
especially recommended for High Energy Physicists who are used to working with awkward arrays. The only
dependency this add is :code:`awkward`. To install this version of the package use:
::

   python -m pip install hepfile[awkward]

You can get the more data science focused tools by installing the :code:`df_tools` and :code:`csv_tools`. These provide
integration with pandas and typical csv files. This is recommended for those who are used to working
with pandas in python. This adds a a :code:`pandas` dependency to the base installation. To install this \
distribution use:
::

   python -m pip install hepfile[pandas]

Finally, to get both the awkward and pandas integration with hepfile (which adds pandas and awkward
to the base installation dependencies) use:
::

   python -m pip install hepfile[all]


For a local installations, typically for developers, follow these steps:

1. Clone this repo
2. Navigate to the top-level directory of this project (probably called hepfile)
3. We then recommend installing with the developer dependencies. To do this run:
   ::

      python -m pip install -e .[dev]

4. Then, run the following commands to setup the pre-commit git hook
   to automatically run our tests before committing!
   ::

      pre-commit install

As a side note, to test developments to this code use the following command in
the top-level directory of this project:
::
   pytest
