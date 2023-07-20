Overview of use case
-----------------------

``hepfile`` is useful for datasets where there are n columns with different numbers
of rows. In more "pythonic" language, you can imagine a dictionary where each key
has a different number of values. For example:
::

   data = {x: [1],
           y: [1, 2],
	   z: ['1', '2', '3']
   }

This can not simply be converted to most common data structures, like a Pandas DataFrame,
or written to a simple homogeneous file structure, like a CSV file. In a more complex case
Let's have an image of a town, with cartoon people here. 

To illustrate how to use hepfile with this example, we imagine a researcher conducting 
a census on a town. Each household in the town has some variable number of people
in it, some variable number of vehicles, and only one residence. The people, vehicles,
and residence all have different data associated with them. How would we record 
these data? Well, to first order, we might decide to record them in multiple spreadsheets or 
multiple .csv files. 

REFERENCE USING NAMES: https://pypi.org/project/names/
(PICTURE BELOW)

.. figure:: /images/household_example_spreadsheet_00.png 
    :scale: 30%
    :alt: Image of spreadsheet

    Click on the image to see a fuller view of the data on the People.

.. figure:: /images/household_example_spreadsheet_01.png
    :scale: 30%
    :alt: Image of spreadsheet

    Click on the image to see a fuller view of the data on the Vehicles.

.. figure:: /images/household_example_spreadsheet_02.png
    :scale: 30%
    :alt: Image of spreadsheet

    Click on the image to see a fuller view of the data on the Residences.


One could also imagine this data stored in a database with each of the csv files as tables.
But the goal is to keep all of this data in one file, so that it is easier for someone to
do analysis. For example, someone might want to know the average number of people per bedroom,
in the homes. Or the average number of vehicles as a function of combined ages of the household
residents. If we have 3 separate files, this is more difficult to work with. What we want is one
file and a way to extract information, collected by *household*.

To do this, we need some way to count the number of people or vehicles in any household,
as well as keep track of what data fields will always have one entry per household (e.g. data
about the residence itself).

One could imagine building a very large [`pandas`](https://pandas.pydata.org/]) dataframe to do this
with a lot of join statements and then use `.groupby()` approach or to store this in a database and
then use a lot of SQL join statements. But we want to store this in a single file so. instead, we will
take our cue from ROOT and particle physicists, who are used to looping over subsets of their data.
