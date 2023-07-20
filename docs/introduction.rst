Introduction
============

Heterogeneous Files in Parallel File (hepfile)
----------------------------------------------

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

.. include:: schema.rst

.. include:: introduction_overview.rst

.. include:: introduction_installation.rst
