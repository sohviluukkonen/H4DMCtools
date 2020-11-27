import csv
import os
import shutil
import argparse
import random
import json 
import H4Dtools_functions as tools

"""

Creates initilised and equilibrated starting file for structure accumulations :

    Input files :
        
        database file (.csv) with solute names 

    Input parameters :

        --load_json : read paremeters from json_file (if not uses default parameters or paremeters defined in the commond line)

        -s, --solutes : database file name
        -f, --infile : reference H4D starting files
        -b, --create_box : creating simulation box from zero (ie. not using reference files)
        -w, --water : water model
        -N : nb of water molecules
        -T : temperature
        -P : pressure
        -C : concentration
        -E, --Ewald : Ewald decomposition
        -dr : g(r) bin size 
        -nmax0 : nmax for solvent molecules
        -ss : solute symmetry
        -nmax1 : nmax for solute molecule
        -eq, --equil : nb of equilibration cycles for des
        -j : job handeler

    Output :

        directory for each solute : solute_name
            input-ini
            acc_{solute_name}_ins0, r_{solute_name}_ins0, acc_{solute_name}_des0, r_{solute_name}_des0
        initialisation_args.out file : recapitulation of initiliasation params in json form
"""

# Parse input params #

parser = argparse.ArgumentParser()
parser.add_argument('--load_json', help="read paremeters from json_file (if not : uses default parameters or paremeters defined in the commond line)" )
#parser.add_argument('--save_json', help="save  paremeters to json_file" )
parser.add_argument('-s','--solutes', default='solutes.csv', help="File containing solute's name, volume and referce HFE (default: %(default)s)" )
parser.add_argument('-f','--infile', default='100tip3p',help="refernce input files (default: %(default)s)" )
parser.add_argument('-b','--create_box', action='store_true', help="create simulation box (default: %(default)s)" )
parser.add_argument('-w','--water', default='TIP3P', help="water force field (default: %(default)s)" )
parser.add_argument('-N', type=int, default=100, help="number of solvent molecules (default: %(default)s)" )
parser.add_argument('-T', type=float, default=298.15, help="temperature (default: %(default)s K)" )
parser.add_argument('-P', type=int, default=100000, help="pressure (default: %(default)s Pa)" )
parser.add_argument('-C', type=float, default=55.4, help="concentration (default: %(default)s M)" )
parser.add_argument('-E','--Ewald', type=int, nargs=3, default=[8,4,4], help="Ewald params KL sr sk (default: %(default)s)" )
parser.add_argument('-nr', type=int, default=500, help="number of bins for g(r) (default: %(default)s Å)" )
parser.add_argument('-dr', type=float, default=0.025, help=" g(r) bin size (default: %(default)s Å)" )
parser.add_argument('-nmax0', type=int, default=6, help="nmax for solvent-solvet (default: %(default)s Å)" )
parser.add_argument('-ss', type=int, default=0, help="solute symmetry (default: %(default)s)" )
parser.add_argument('-nmax1', type=int, default=0, help="nmax for solute (default: %(default)s sqrt(kT/M)" )
parser.add_argument('-dt',type=float, default=0.02, help="time step (default: %(default)s sqrt(M/kT)Å" )
parser.add_argument('-eq','--equil', type=int, default=10000, help="nb of MC equilibartion cycles for destruction (default: %(default)s kT)" )
parser.add_argument('-j', default="slurm", help=" Job handeling system : slumr or loadleveler  (default: %(default)s)" )
parser.add_argument('-ns','--nostart', action='store_true', help="do not launch jobs (default: %(default)s)" )
args = parser.parse_args()
print(args)

# Read parameters from .json file if given
if args.load_json: args = tools.json2args(args.load_json)

# Save parameters in json.out file
tools.args2json('params_ini.out',args)

# Load solutes names
with open(args.solutes, 'r') as f:
    molecules = [row[0] for row in csv.reader(f)] 

# Create paths to solutes and input files
home_dir = "%s" % os.getcwd()
input_dir = os.path.join(home_dir,'input-files')
sol_dir = os.path.join(home_dir,'solutein')

# Iterate over solutes
for mol in molecules:

    # Create directory per solute
    mol_dir = os.path.join(home_dir,mol)
    tools.mkdir_p(mol)

    # Copy input files
    shutil.copy(os.path.join(input_dir,'h4dmc.x'),mol_dir)
    shutil.copy(os.path.join(input_dir,'dummy.in'),mol_dir)
    shutil.copy(os.path.join(input_dir,'dummy.top'),mol_dir)
    shutil.copy(os.path.join(sol_dir,mol + '.in'),mol_dir)
    if os.path.isfile(os.path.join(sol_dir,mol+'.top')) == True:
        shutil.copy(os.path.join(sol_dir,mol + '.top'),mol_dir)

    if args.infile is not None :
        shutil.copy(os.path.join(input_dir,'acc_' + args.infile),mol_dir)
        shutil.copy(os.path.join(input_dir,'r_' + args.infile),mol_dir)

    # Crete and launch H4D initialisation
    tools.create_structure_initialisation_input(args,solute=mol,mol_dir=mol_dir)

    if args.nostart == True :
        continue
    else :
        if args.j == "slurm" :
            shutil.copy(os.path.join(input_dir,'job-ini'),mol_dir)
            job_file = os.path.join(mol_dir,'job-ini')
            os.system("cd {0}; sbatch {1}; cd ..".format(mol_dir,job_file))
        if args.j == "loadleveler" :
            shutil.copy(os.path.join(input_dir,'job-ini'),mol_dir)
            job_file = os.path.join(mol_dir,'job-ini')
            os.system("cd {0}; llsubmit {1}; cd ..".format(mol_dir,job_file))



