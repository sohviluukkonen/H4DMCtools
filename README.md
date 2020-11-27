# H4DMCtools

Python wrapper to accumulate hydration free energies OR hydration structures of a set of solutes with H4D-MC code.

I. Accumulation of hydration free energies :
	
	1-initialisation.py
	2-production.py
	3-analysis.py
	H4Dtools_functions.py

	solutes.csv file : solute names, volumes and reference HFE
	solutein directory : strutcure files (.in) and optionally topology files (.top)
	input-files directory : additional general input files

II. Accumulation of structures :

	1-initialisation-structure.py
	2-production-structure.py
	H4Dtools_functions.py

	solutes.csv : solute names
	solutein directory : strutcure files (.in) and optionally topology files (.top)
        input-files directory : additional general input files

Notes : 
	
	- h4dmc.x needs to compiled add and added to input-files on each different computer
	- h4dmc.x is the flexible version of the code for all calculation

TODO :
	- add modifications done to the rigid version of h4dmc to the flexible version 

