===========
Basic Usage
===========

Basics of File Structure
------------------------

In this section we will be continuing with the `example of households from the introduction <https://hepfile.readthedocs.io/en/latest/introduction.html#overview-of-use-case>`_
but diving into more details about writing and reading hepfiles with the data. In hepfile,
all the data can be grouped into **buckets**, which in this case can be associated with
households (and the Household ID). *people* and *vehicles* would be separated **groups**, with all their data
being contained in **datasets** inside each group. With *houses*, there are two separate options:
one could either make a new group *houses*, or you could include all of its data in the
**_SINGLETONS_GROUP_**, a special group designed to store all datasets where each bucket has one and only one
entry from it. Because we require every household to only have one house, each household has only one entry
from *# of bedrooms*, for example.

.. include:: writing.rst

.. include:: reading.rst
