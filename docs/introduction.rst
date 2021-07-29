Introduction
============

In high energy physics, experiments require file formats that can accomodate 
heterogeneity (each collection event can have differing amounts of data collected)
and size (since HEP experiments can generate petabytes of data). Although the current
file format of choice is ROOT, a file format developed by CERN, we believe that
HDF5, which is a portable and more commonly used file format outside of HEP,
has promise in being a new standard. 

The only issue is that HDF5 works best with homogenous data formats, where each
dataset occupies an n by m chunk of memory. This is not necessarily the case
for HEP data, but we addressed this issue using an organizational method outlined
in our schema.


Overview of use case
-----------------------

Here

Installation quickstart 
-----------------------

You can install ``hepfile`` one of two different ways: using ``pip`` or ``flit``.

####
pip
####
::

    pip install hepfile

####
flit
####

``flit`` is used to do a local install if you have downloaded the source
code to your local machine. This is particularly useful if you are developing
or extending ``hepfile``.

First make sure you have `flit <https://flit.readthedocs.io/en/latest/>`_ installed. 
You will also need to have `autodoc <https://pypi.org/project/autodoc/>`_ installed for 
the documentation to also be locally generated. 

Once those are installed, clone the `hepfile <https://github.com/mattbellis/hepfile>`_ repository and go
into the ``hepfile`` directory. From there run the command::


    flit install

