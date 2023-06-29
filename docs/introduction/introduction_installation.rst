Installation quickstart 
-----------------------

You can install ``hepfile`` using ``pip``.

####
pip
####
::

    pip install hepfile

###################
Local Installations
###################

To install locally for development, follow these steps:
For local builds for testing follow these steps:
   
   1. Clone this repo
   2. Navigate to the top-level directory of this project (probably called hepfile)
   3. Run:
      ::
	 pip install -e .
   4. Then, run the following commands to setup the pre-commit git hook
      to automatically run our tests before committing!
      ::
	 chmod a+x pre-commit-tests.sh
	 ln -s ../../pre-commit-tests.sh .git/hooks/pre-commit

