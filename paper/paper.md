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
  - name: Noah Franz
    orcid: 0000-0003-4537-3575
    affiliation: 1
  - name: Matt Dreyer
    orcid: 0000-0002-7877-2858
    affiliation: 2
  - name: Willow Hagen
    orcid: 0000-0001-6637-2112
    affiliation: "1"
affiliations:
 - name: Siena College
   index: 1
 - name: Cornell University
   index: 2
date: "29 July 2021"
bibliography: paper.bib

---

# Summary
Most file formats excel when the data exist in some simple, homogenous n x m block structure. However, High Energy Physics (HEP) datasets are challenging for many file formats because of the heterogeneous nature of the dataset: instead of an n x m structure they have n columns with variable lengths. An example in HEP could be a beam-collision interaction that produces 3 electrons and 2 muons while the next interaction may produce 12 electrons and no muons. A non-HEP example might involve trying to store information about households: one household may have 2 adults, 7 children, and 2 vehicles, while another household may have 1 adult, 1 child, and no vehicles. A database of these households is difficult to export to a single file in its current structure because of the different lengths of the tables. The solution in the HEP community has been to make use of the self-contained ROOT toolkit [@ROOT], but this can be limiting for users who may
want to interface with the broader computing/data science community, most of whom have little to no experience with ROOT files. While inspired
by the experiences of HEP analyses, we believe that the *hepfile* file format could be useful to analysts
across many disciplines, particularly those who work with irregularly shaped datasets that might normally
be analyzed with multiple files or stored in a database.


*hepfile* (Heterogeneous Entries in Parallel - file) is a data description for organizing heterogeneous datasets such that they can be stored and extracted in an HDF5 [@HDF5] file. *hepfile* is the successor to an earlier software, named *h5hep* [@h5hep], which was used in an outreach website, the Particle Physics Playground [@ppp]. *hepfile* has now replaced *h5hep* for that outreach website. Additionally, one of the authors of this package uses *hepfile* for their analysis with the BaBar and CMS particle physics experiments at SLAC and CERN, respectively.

*hepfile* provides the structure and python functionality to work with heterogeneous ROOT-like data stored in the more flexible HDF5 file format. In *hepfile*,e provide methods to pack and unpack heterogeneous data into / out of an HDF5 file making use of standard python packages [@numpy; @h5py], as well as some optional helper tools to interface with other python-based analysis packages [@pandas; @awkward]. This gives users access to a ROOT-file-like functionality without touching the independent ROOT ecosystem using native python tools. Additionally, HDF5 is particularly advantageous because the file format is accessible across a variety of programming languages allowing for *hepfile* files to be accessed in any language that supports HDF5.

# Statement of need
To store and analyze the heterogeneous datasets that come out of particle physics experiments, a group of HEP researchers developed the ROOT [@ROOT] software kit in the mid-90’s in C++. ROOT was envisioned as a monolithic toolkit that defined its own file structure and had an extensive library of analysis classes, functions to fit data distributions, and its own plotting and visualization tools. ROOT’s inflexibility has been both a benefit to and a source of frustration for some users. On the one hand, the community has a common toolkit to work with; on the other hand, users can feel “locked in” to the ROOT ecosystem, making it difficult to interface with the many modern software tools developed since ROOT’s inception. There are newer packages that can extract data from ROOT files without importing the entire ROOT package [@uproot], but writing the data back to ROOT-files is still not fully supported at the time of this paper.

*hepfile* solves some of these problems by utilizing a widely-used file format, HDF5 [@HDF5], and defining a way to pack/unpack the data that looks and feels familiar to ROOT-users while remaining straightforward to someone who has never used ROOT before. This makes *hepfile* not only useful in HEP but also in other areas of data science that include heterogeneous datasets, where the solution instead requires a database.
In addition, because the underlying file is HDF5, a user can interact with and inspect the file with any other HDF5-based tools, including those provided by the HDF5 group or other languages that have HDF5-APIs implemented in them like C++ and Julia. This language-independent nature of the *hepfile* structure enables it to be used alongside new software packages and languages as they come along in the future.

# Acknowledgements
We acknowledge contributions from Siena College student Ryan Mikulec in the earliest stages of this project, as well as helpful discussions with many, many colleagues including, but not limited to Jim Pivarski and John Cummings.

Matt Bellis, Noah Franz, and Willow Hagen have received support for work related to *hepfile* provided by NSF grants EPP-1913923 and / or EPP-1608779. Matt Dreyer received support for work related to *hepfile* from NSF grants EPP-1913923 and OAC-1450377 (DIANA/HEP).

# References
