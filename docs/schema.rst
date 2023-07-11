Schema
------

Heterogenous Data 
^^^^^^^^^^^^^^^^^

We assume that data that we collect is composed of (insert some term for particle, 
chair, etc.) each carrying a certain number of attributes. Each ___ is associated 
with some increasing counter. In HEP, this counter is events. Each event can
have an arbitrary number of particles of any type, making this data heterogenous. 

Homogenous File 
^^^^^^^^^^^^^^^^^

To make this data homogenous, we can create n by m chunks of data for each type 
of particle, where n is the total number of this particle in all of the events, 
and the specific row for each of the particles contains all of the attributes 
for that particle in the original data.

We also create a list for each type of particle whose length is the total number
of events. At position *i*, we have the data for how many particles of said type
appeared in event *i*. 
