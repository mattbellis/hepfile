===========
Basic Usage
===========

Basics of File Structure
------------------------

In hepfile, all the data can be grouped into **buckets**, which in this case can be associated with
households (and the Household ID). *people* and *vehicles* would be separate **groups**, with all their data
being contained in **datasets** inside each group. With *houses*, there are two separate options:
one could either make a new group *houses*, or you could include all of its data in the 
**_SINGLETONS_GROUP_**, a special group designed to store all datasets where each bucket has one and only one
entry from it. Because we require every household to only have one house, each household has only one entry
from *# of bedrooms*, for example.

.. include:: writing.rst

.. include:: reading.rst



