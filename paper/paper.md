---
title: 'hepfile: A data and file description for heterogenous-length data, implemented in python and HDF5'
tags:
  - Python
  - HEP
  - high energy physics
  - HDF5
  - h5py
  - education
  - outreach
  - file formats
  - big data
authors:
  - name: Matt Bellis
    orcid: 0000-0002-6353-6043
    affiliation: 1
  - name: Matt Dreyer
    orcid: 0000-0002-7877-2858
    affiliation: 2
  - name: Willow Hagen
    orcid: 0000-0001-6637-2112
    affiliation: "3,1"
  - name: Noah Franz
    orcid: 0000-0003-4537-3575
    affiliation: 1
affiliations:
 - name: Siena College
   index: 1
 - name: Cornell University
   index: 2
 - name: Carnegie Mellon University
   index: 3
date: "29 July 2021"
bibliography: paper.bib

---

# Summary

High Energy Physics (HEP) datasets are
challenging for many file formats because of the inhomogeneous nature
of the dataset: one event may have 3 jets and 2 muons and the next
event may have 12 jets and no muons. Most file formats excel when the
data exists in some simple, homogenous n x m block structure. 
The TFile and TTree
objects in ROOT handle these datasets incredibly well but require users
to import the entire ROOT ecosystem just to read the files, locking out
users from other communities that do not use ROOT. `hepfile` 
(Heterogeneous Entries in Parallel - file) is a data description for
organizing this type of data, a API definition for interfacing with these data,
and a description of how to pack this into a file. These abstract definitions
have been implemented with a python API and making use of the HDF5 file format.wrapper to the HDF5 format
that gives users access to the ROOT functionality without ROOT and
making use of native python tools. The performance of this tool and its
application to non-HEP datasets will be presented.


# Statement of need

ROOT is frustrating [@ROOT].

Used for Particle Physics Playground [@ppp].

# Description

Grew out of `h5hep` [@h5hep].

# Implementation

We used `h5py` [@h5py].

We used `numpy` [@numpy].

# Availability and Installation
`hepfile` is open-source software made available under the Apache License, Version 2.0.
Documentation can be found on ReadTheDocs
at [https://hepfile.readthedocs.io/](https://hepfile.readthedocs.io/).
It can be installed from PyPI as
```
pip install hepfile
```
or from its GitHub repository using `flit`.


# Acknowledgements

We acknowledge contributions from Siena College student Ryan Mikulec in the
earliest stages of this project, as well as hepful discussions with many, many 
colleagues.

Matt Bellis and Willow Hagen have received support for work related to 
`hepfile` provided by NSF grants EPP-1913923 and EPP-1608779.
Matt Dreyer received support for work related to `hepfile` from 
NSF grants EPP-1913923 and OAC-1450377 (DIANA/HEP).

# References
