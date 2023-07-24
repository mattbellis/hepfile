Introduction
============

Heterogeneous Entries in Parallel File (hepfile)
----------------------------------------------

High energy physics (HEP) experiments involve colliding subatomic particles at
close to the speed of light, and looking at the particles produced by these collisions.
Each collision (or *event*, in HEP parlance), can produce a different number of
of particles, thanks to the probabilistic nature of quantum mechanics.
One collision could produce 3 muons, 2 electrons, 9 pions, and 12 photons, and
the next colliions could produce 7 muons, 0 electrons, 22 pions, and 33 photons.
These datasets require file formats that can accomodate
this type of numerical heterogeneity, since we can't easily break this down into
a simple *n x m* array. Simply put, HEP datasets don't lend themselves
to `.csv` files or spreadsheet analysis.

This challenge was solved more than 20 years ago with the widespread
adoption of the `ROOT <https://root.cern/>`_ file format, a format tied to the
ROOT analaysis toolkit at `CERN <https://www.home.cern/>`_. However, the
monolithic and HEP-specific nature of ROOT has made it challenging at
times to share data with the broader computing community.
We believe that HDF5, a portable and commonly used file format outside of HEP,
holds promise in being a useful file format for many HEP analysts.

One issue is that HDF5 works best with homogenous data formats, where each
dataset occupies an *n x m* chunk of memory. To work with

WE PROVIDE DICTIONARY TO WORK WITH TO DEAL WITH SUBSETS OF THE DATA.

METADATA AND HEADER.

.. include:: schema.rst

.. include:: introduction_overview.rst

.. include:: introduction_installation.rst
